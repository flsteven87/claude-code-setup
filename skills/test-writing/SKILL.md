---
name: test-writing
description: 當用戶要求寫測試、unit test、integration test、e2e test、測試代碼時觸發此 skill
status: active
tags: [core, testing]
alternative: superpowers:test-driven-development  # 更完整版本
updated: 2026-02-07
---

# Test Writing Skill

撰寫高品質、可維護的測試代碼。

## 測試金字塔

```
        /\
       /  \      E2E Tests (少量)
      /----\     - 完整用戶流程
     /      \
    /--------\   Integration Tests (適量)
   /          \  - 模組間互動
  /------------\ 
 /              \ Unit Tests (大量)
/________________\- 單一函數/元件
```

## 測試命名規範

### 格式
```
describe('[被測試的單元]', () => {
  it('should [預期行為] when [條件/情境]', () => {
    // ...
  });
});
```

### 範例
```typescript
describe('UserService', () => {
  describe('createUser', () => {
    it('should create a new user when valid data is provided', () => {});
    it('should throw ValidationError when email is invalid', () => {});
    it('should hash password before saving', () => {});
  });
});
```

## AAA 模式

每個測試遵循 Arrange-Act-Assert 結構：

```typescript
it('should calculate total with discount', () => {
  // Arrange - 準備測試資料和環境
  const cart = new Cart();
  cart.addItem({ price: 100, quantity: 2 });
  const discount = 0.1; // 10% off

  // Act - 執行被測試的行為
  const total = cart.calculateTotal(discount);

  // Assert - 驗證結果
  expect(total).toBe(180);
});
```

## 測試類型指南

### Unit Tests

```typescript
// ✅ 好的 unit test
describe('formatCurrency', () => {
  it('should format number with currency symbol', () => {
    expect(formatCurrency(1234.5)).toBe('$1,234.50');
  });

  it('should handle zero', () => {
    expect(formatCurrency(0)).toBe('$0.00');
  });

  it('should handle negative numbers', () => {
    expect(formatCurrency(-100)).toBe('-$100.00');
  });
});
```

特點：
- 測試單一函數/方法
- 不依賴外部服務
- 快速執行（毫秒級）

### Integration Tests

```typescript
describe('UserRepository', () => {
  let repository: UserRepository;
  let db: TestDatabase;

  beforeEach(async () => {
    db = await TestDatabase.create();
    repository = new UserRepository(db);
  });

  afterEach(async () => {
    await db.cleanup();
  });

  it('should persist and retrieve user', async () => {
    const user = { name: 'John', email: 'john@example.com' };
    
    const created = await repository.create(user);
    const found = await repository.findById(created.id);
    
    expect(found).toMatchObject(user);
  });
});
```

特點：
- 測試模組間互動
- 可能使用真實資料庫（測試環境）
- 需要適當的 setup/teardown

### E2E Tests

```typescript
describe('User Registration Flow', () => {
  it('should allow new user to register and login', async () => {
    await page.goto('/register');
    
    await page.fill('[name="email"]', 'new@example.com');
    await page.fill('[name="password"]', 'SecurePass123');
    await page.click('button[type="submit"]');
    
    await expect(page).toHaveURL('/dashboard');
    await expect(page.locator('.welcome-message')).toContainText('Welcome');
  });
});
```

特點：
- 模擬真實用戶操作
- 測試完整流程
- 執行時間較長

## 測試品質檢查清單

### 覆蓋率考量
- [ ] Happy path（正常流程）
- [ ] Edge cases（邊界條件）
- [ ] Error cases（錯誤處理）
- [ ] Null/undefined 處理

### 測試品質
- [ ] 測試名稱清晰描述預期行為
- [ ] 每個測試只驗證一件事
- [ ] 測試之間互相獨立
- [ ] 不依賴測試執行順序
- [ ] 避免測試中的邏輯（if/else）

### Mocking 原則
```typescript
// ✅ Mock 外部依賴
jest.mock('./external-api');

// ❌ 避免 mock 被測試的單元本身
// ❌ 避免過度 mock 導致測試無意義
```

## 常見測試場景模板

### 非同步操作
```typescript
it('should fetch data successfully', async () => {
  const result = await fetchData();
  expect(result).toBeDefined();
});
```

### 錯誤處理
```typescript
it('should throw error when input is invalid', () => {
  expect(() => validate(null)).toThrow('Input is required');
});

// 非同步錯誤
it('should reject when API fails', async () => {
  await expect(fetchData('invalid')).rejects.toThrow('Not found');
});
```

### Snapshot 測試
```typescript
it('should render correctly', () => {
  const tree = render(<Component prop="value" />);
  expect(tree).toMatchSnapshot();
});
```
