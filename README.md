# DexilonBridge_v10

Layer 1 Dexilon bridge smart contract.

## Methods

### addValidators

```solidity
function addValidators(address[] newValidators) external nonpayable
```

Add new validators to the list of active validatos

*Only owner*

#### Parameters

| Name | Type | Description |
|---|---|---|
| newValidators | address[] | Array of addresses assigned to new validators

### batchUpdateAvailableBalances

```solidity
function batchUpdateAvailableBalances(address _tokenAddress, address[] users, uint256[] balanceUpdates, uint256 batchId, bytes[] signatures) external nonpayable
```

Updates user balances available to be claimed

*Updates are additive*

#### Parameters

| Name | Type | Description |
|---|---|---|
| _tokenAddress | address | address of the supported token
| users | address[] | array of user addresses to be updated
| balanceUpdates | uint256[] | array of additive balance updates for specified users
| batchId | uint256 | unique id of the batch
| signatures | bytes[] | validators signatures for the batch

### deposit

```solidity
function deposit(address _tokenAddress, uint256 amount) external nonpayable
```

Deposit token into contract

#### Parameters

| Name | Type | Description |
|---|---|---|
| _tokenAddress | address | address of the supported token
| amount | uint256 | Amount of token in smallest units

### getActiveValidators

```solidity
function getActiveValidators() external view returns (address[])
```

Get the list of active

#### Returns

| Name | Type | Description |
|---|---|---|
| _0 | address[] | Array of active validators addresses

### getAvailableBalance

```solidity
function getAvailableBalance(address _tokenAddress, address userAddress) external view returns (uint256)
```

Available balance to be claimed by user

#### Parameters

| Name | Type | Description |
|---|---|---|
| _tokenAddress | address | address of the supported token
| userAddress | address | address of the user

#### Returns

| Name | Type | Description |
|---|---|---|
| _0 | uint256 | User balance for specified token available to be claimed

### getLockedBalance

```solidity
function getLockedBalance(address _tokenAddress) external view returns (uint256)
```

Total locked balance for specified token

*Differs from token balance of this contract taking into account available for users*

#### Parameters

| Name | Type | Description |
|---|---|---|
| _tokenAddress | address | address of the supported token

#### Returns

| Name | Type | Description |
|---|---|---|
| _0 | uint256 | Amount of token locked in this contract

### getSupportedTokens

```solidity
function getSupportedTokens() external view returns (address[])
```

Get list of supported tokens

#### Returns

| Name | Type | Description |
|---|---|---|
| _0 | address[] | Array of tokens addresses supported by this contract for deposit

### owner

```solidity
function owner() external view returns (address)
```

*Returns the address of the current owner.*

#### Returns

| Name | Type | Description |
|---|---|---|
| _0 | address | undefined

### pause

```solidity
function pause() external nonpayable
```

Pause deposit and withdraw of tokens

*Only Owner when not paused*

### paused

```solidity
function paused() external view returns (bool)
```

*Returns true if the contract is paused, and false otherwise.*

#### Returns

| Name | Type | Description |
|---|---|---|
| _0 | bool | undefined

### removeValidators

```solidity
function removeValidators(address[] retiredValidators) external non-payable
```

Remove validators from the list of active validators

*Only owner*

#### Parameters

| Name | Type | Description |
|---|---|---|
| retiredValidators | address[] | Array of addresses of validators to be removed

### renounceOwnership

```solidity
function renounceOwnership() external non-payable
```

*Leaves the contract without owner. It will not be possible to call `onlyOwner` functions anymore. Can only be called by the current owner. NOTE: Renouncing ownership will leave the contract without an owner, thereby removing any functionality that is only available to the owner.*

### setSupportedToken

```solidity
function setSupportedToken(address _tokenAddress, bool isSupported) external nonpayable
```

Add address of the token supported or turn support off

#### Parameters

| Name | Type | Description |
|---|---|---|
| _tokenAddress | address | address of the supported token
| isSupported | bool | true - accept deposits, false - stop accepting deposits

### transferOwnership

```solidity
function transferOwnership(address newOwner) external non-payable
```

*Transfers ownership of the contract to a new account (`newOwner`). Can only be called by the current owner.*

#### Parameters

| Name | Type | Description |
|---|---|---|
| newOwner | address | undefined

### unpause

```solidity
function unpause() external nonpayable
```

Unpause deposit and withdraw of tokens

*Only Owner when paused*

### withdraw

```solidity
function withdraw(address _tokenAddress) external nonpayable
```

Withdraw available token balance

*no restriction to withdraw if token support is discontinued*

#### Parameters

| Name | Type | Description |
|---|---|---|
| _tokenAddress | address | address of the supported token

## Events

### BatchRecorded

```solidity
event BatchRecorded(uint256 indexed batchId, address indexed token, address receivedFrom, uint256 timestamp)
```

#### Parameters

| Name | Type | Description |
|---|---|---|
| batchId `indexed` | uint256 | undefined |
| token `indexed` | address | undefined |
| receivedFrom  | address | undefined |
| timestamp  | uint256 | undefined |

### Deposit

```solidity
event Deposit(address indexed depositor, address indexed token, uint256 amount, uint256 timestamp)
```

#### Parameters

| Name | Type | Description |
|---|---|---|
| depositor `indexed` | address | undefined |
| token `indexed` | address | undefined |
| amount  | uint256 | undefined |
| timestamp  | uint256 | undefined |

### OwnershipTransferred

```solidity
event OwnershipTransferred(address indexed previousOwner, address indexed newOwner)
```

#### Parameters

| Name | Type | Description |
|---|---|---|
| previousOwner `indexed` | address | undefined |
| newOwner `indexed` | address | undefined |

### Paused

```solidity
event Paused(address account)
```

#### Parameters

| Name | Type | Description |
|---|---|---|
| account  | address | undefined |

### Unpaused

```solidity
event Unpaused(address account)
```

#### Parameters

| Name | Type | Description |
|---|---|---|
| account  | address | undefined |

### Withdraw

```solidity
event Withdraw(address indexed depositor, address indexed token, uint256 amount, uint256 timestamp)
```

#### Parameters

| Name | Type | Description |
|---|---|---|
| depositor `indexed` | address | undefined |
| token `indexed` | address | undefined |
| amount  | uint256 | undefined |
| timestamp  | uint256 | undefined |
