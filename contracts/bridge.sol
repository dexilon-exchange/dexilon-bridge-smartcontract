// SPDX-License-Identifier: UNLICENSED

pragma solidity 0.8.16;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import "@openzeppelin/contracts/utils/cryptography/ECDSA.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/Pausable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/utils/cryptography/EIP712.sol";

contract DexilonBridge_v10 is EIP712, Ownable, Pausable, ReentrancyGuard {
    using SafeERC20 for IERC20;
    using ECDSA for bytes32;

    address[] internal supportedTokens;
    
    mapping (address=>bool) internal isTokenSupported;

    // token => user => balance
    mapping(address => mapping (address => uint256)) internal usersAvailableBalances;
    mapping(address => uint256) internal lockedBalances; // per token

    address[] internal validators;
    uint256 internal validatorsCounter;
    mapping(address => bool) internal isValidator;

    // batchId => token => true/false
    mapping(uint256 => mapping (address => bool) ) internal isBatchIdRecorded;

    
    event Deposit(
        address indexed depositor,
        address indexed token,
        uint256 amount,
        uint256 timestamp
    );

    event Withdraw(
        address indexed depositor,
        address indexed token,
        uint256 amount,
        uint256 timestamp
    );

    event BatchRecorded(
        uint256 indexed batchId,
        address indexed token,
        address receivedFrom,
        uint256 timestamp
    );
    
    
    constructor(string memory name, string memory version) EIP712(name, version)  {

    }

    /**
     * @notice Add address of the token supported or turn support off
     * @param _tokenAddress address of the supported token
     * @param isSupported true - accept deposits, false - stop accepting deposits
     */
    function setSupportedToken(address _tokenAddress, bool isSupported) external onlyOwner {
        uint256 indexInArray;
        uint256 arrayLength;

        require(_tokenAddress != address(0), "Zero token address!");

        isTokenSupported[_tokenAddress] = isSupported;

        // if isSupported is true and token address is new
        // adding to the list of supported tokens
        if (isSupported && !isAddressInArray(_tokenAddress, supportedTokens)) {
            supportedTokens.push(_tokenAddress);
        }
        // if isSupported is false and token address is in supported list
        // removing from the list of supported tokens
        if (!isSupported && isAddressInArray(_tokenAddress, supportedTokens)) {
            arrayLength = supportedTokens.length;
            for (uint256 i=0; i < arrayLength; i++) {
                if (_tokenAddress == supportedTokens[i]) {
                    indexInArray = i;
                    break;
                }
            }
            supportedTokens[indexInArray] = supportedTokens[arrayLength-1];
            supportedTokens.pop();
        }
        
    }

    function isAddressInArray(address _address, address[] memory _array) internal pure returns (bool) {
        uint256 arrayLength;
        arrayLength = _array.length;
        for (uint256 i=0; i < arrayLength; i++) {
            if (_address == _array[i]) {
                return true;
            }
        }
        return false;
    }

    /**
     * @notice Get list of supported tokens
     * @return Array of tokens addresses supported by this contract for deposit
     */
    function getSupportedTokens() external view returns (address[] memory) {
        return supportedTokens;
    }


    /**
     * @notice Deposit token into contract
     * @param _tokenAddress address of the supported token
     * @param amount Amount of token in smallest units
     */
    function deposit(address _tokenAddress, uint256 amount) external whenNotPaused nonReentrant {

        require(isTokenSupported[_tokenAddress], "Token not supported!");

        // User mapping initialization for reducing peak gas costs for the batch
        if (usersAvailableBalances[_tokenAddress][msg.sender] == 0) {
            usersAvailableBalances[_tokenAddress][msg.sender] = uint256(1);
        }
        
        lockedBalances[_tokenAddress] += amount;

        emit Deposit(msg.sender, _tokenAddress, amount, block.timestamp);

        IERC20(_tokenAddress).safeTransferFrom(msg.sender, address(this), amount);
    }

    /**
     * @notice Available balance to be claimed by user
     * @param _tokenAddress address of the supported token
     * @param userAddress address of the user
     * @return User balance for specified token available to be claimed
     */
    function getAvailableBalance(address _tokenAddress, address userAddress) external view returns (uint256) {
        if (usersAvailableBalances[_tokenAddress][userAddress] != 0) {
            return usersAvailableBalances[_tokenAddress][userAddress] - 1;
        } else {
            return 0;
        }
    }

    /**
     * @notice Total locked balance for specified token
     * @dev Differs from token balance of this contract taking into account available for users
     * @param _tokenAddress address of the supported token
     * @return Amount of token locked in this contract
     */
    function getLockedBalance(address _tokenAddress) external view returns (uint256) {
        return lockedBalances[_tokenAddress];
    }

    /**
     * @notice Updates user balances available to be claimed
     * @dev Updates are additive
     * @param _tokenAddress address of the supported token
     * @param users array of user addresses to be updated
     * @param balanceUpdates array of additive balance updates for specified users
     * @param batchId unique id of the batch
     * @param signatures validators signatures for the batch
     */
    function batchUpdateAvailableBalances(address _tokenAddress, address[] memory users, uint256[] memory balanceUpdates, uint256 batchId, bytes[] memory signatures) external nonReentrant {

        uint256 verifiedSignatures;
        uint256 updatesTotal;
        uint256 signaturesLength;
        uint256 usersLength;
        bytes32 txEthHash;

        require(isValidator[msg.sender], "Only validator!");
        require(validatorsCounter > 2, "Not enough validators!");
        require(!isBatchIdRecorded[batchId][_tokenAddress], "Batch already recorded!");

        usersLength = users.length;
        
        require(usersLength == balanceUpdates.length, "Lists length do not match!");

        // Getting number of signatures that belong to active validators
        txEthHash = getEthHash(getHashForBatch(_tokenAddress, users, balanceUpdates, batchId));
        signaturesLength = signatures.length;

        for (uint256 i=0; i < signaturesLength; i++){
            // check if signature is unique
            if (!isSignatureUniqueInArray(signatures[i], signatures)) {
                delete signatures[i]; // delete repeated signature
            } else {
                if ( isValidator[ECDSA.recover(txEthHash, signatures[i])] ) {
                    verifiedSignatures++;
                }
            }
        }
        require( (verifiedSignatures * 3)/validatorsCounter >= 2, "Not enough signatures!");
        
        
        isBatchIdRecorded[batchId][_tokenAddress] = true;

        // Applying batch balances updates
        for (uint256 i=0; i < usersLength; i++) {
            usersAvailableBalances[_tokenAddress][users[i]] += balanceUpdates[i];
            updatesTotal += balanceUpdates[i];
        }

        require( lockedBalances[_tokenAddress] >= updatesTotal, "Not enough locked token!");
        lockedBalances[_tokenAddress] -= updatesTotal;

        emit BatchRecorded(batchId, _tokenAddress, msg.sender, block.timestamp);

    }

    function isSignatureUniqueInArray(bytes memory signature, bytes[] memory signatureArray) internal pure returns (bool) {

        uint256 arrayLength = signatureArray.length;
        uint256 counter;

        for (uint256 i=0; i < arrayLength; i++) {
            if (keccak256(signature) == keccak256(signatureArray[i])) {
                counter++;
                if (counter > 1) {
                    return false;
                }
            }
        }

        return counter == 1;
    }

    /**
     * @notice Add new validators to the list of active validatos
     * @dev Only owner
     * @param newValidators Array of addresses assigned to new validators
     */
    function addValidators(address[] memory newValidators) external onlyOwner {
        uint256 newValidatorsLength;

        newValidatorsLength = newValidators.length;

        for (uint256 i=0; i < newValidatorsLength; i++) {

            require(newValidators[i] != address(0), "Cannot be zero address!");

            if (!isValidator[newValidators[i]]) {

                isValidator[newValidators[i]] = true;
                validatorsCounter++;
                validators.push(newValidators[i]);
            }
        }
    }

    /**
     * @notice Remove validators from the list of active validators
     * @dev Only owner
     * @param retiredValidators Array of addresses of validators to be removed
     */
    function removeValidators(address[] memory retiredValidators) external onlyOwner {

        uint256 indexInArray;
        uint256 retiredValidatorsLength;

        retiredValidatorsLength = retiredValidators.length;

        for (uint256 i=0; i < retiredValidatorsLength; i++) {
            if (isValidator[retiredValidators[i]]) {

                delete isValidator[retiredValidators[i]];
                // removing validator from the list of active validators
                for (uint256 j=0; j < validatorsCounter; j++) {
                    if (retiredValidators[i] == validators[j]) {
                        indexInArray = j;
                        break;
                    }
                }
                validators[indexInArray] = validators[validatorsCounter-1];
                validators.pop();
                validatorsCounter--;

            }
        }

    }

    /**
     * @notice Get the list of active 
     * @return Array of active validators addresses
     */
    function getActiveValidators() external view returns (address[] memory) {
        return validators;
    }

    function getEthHash(bytes32 _hash) internal pure returns (bytes32) {
        return ECDSA.toEthSignedMessageHash(_hash);
    }

    function getHashForBatch(address _tokenAddress, address[] memory users, uint256[] memory balances, uint256 batchId) internal view returns (bytes32) {
        return keccak256(abi.encodePacked(_domainSeparatorV4(), _tokenAddress, users, balances, batchId));
    }


    /**
     * @notice Withdraw available token balance
     * @dev no restriction to withdraw if token support is discontinued
     * @param _tokenAddress address of the supported token
     */
    function withdraw(address _tokenAddress) external whenNotPaused nonReentrant {

        uint256 withdrawAmount;
        
        withdrawAmount = usersAvailableBalances[_tokenAddress][msg.sender];
        require(withdrawAmount > 1, "No balance!");
        
        usersAvailableBalances[_tokenAddress][msg.sender] = uint256(1);
        IERC20(_tokenAddress).safeTransfer(msg.sender, withdrawAmount - 1);

        emit Withdraw(msg.sender, _tokenAddress, withdrawAmount - 1, block.timestamp);
    }

    /**
     * @notice Pause deposit and withdraw of tokens
     * @dev Only Owner when not paused
     */ 
    function pause() external whenNotPaused onlyOwner {
        _pause();
    }

    /**
     * @notice Unpause deposit and withdraw of tokens
     * @dev Only Owner when paused
     */ 
    function unpause() external whenPaused onlyOwner {
        _unpause();
    }

}