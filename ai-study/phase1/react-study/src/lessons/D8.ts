/*
  D8：TypeScript 类型系统练习

  规则：
  所有 TODO 由主公亲手完成。除非课程明确要求，否则不要使用 `any`。
*/

/*
  Part 1：建模一个接口数据对象

  TODO：定义一个 Post interface。

  要求：
  - id 是只读 number
  - userId 是 number
  - title 是 string
  - body 是 string
*/
interface Post {
  readonly id: number;
  userId: number;
  title: string;
  body: string;
}

/*
  Part 2：从 Post 派生新类型

  TODO:
  - PostSummary 只保留 id 和 title。
  - PostCreate 去掉 id，因为 id 由服务端生成。
  - PostPatch 让 title 和 body 变成可选字段，用于局部更新。
  - PostMap 用数字 id 映射到 Post 值。
*/
type PostSummary = Pick<Post, "id" | "title">;
type PostCreate = Omit<Post, "id">;
type PostPatch = Partial<Pick<Post, "title" | "body">>;
type PostMap = Record<number, Post>;

/*
  Part 3：用泛型保留输入和输出的类型关系

  TODO: first<T>(items: T[]): T | undefined

  预期行为：
  - first(["a", "b"]) 的类型是 string | undefined
  - first([1, 2]) 的类型是 number | undefined

  TODO: indexById<T extends { id: number }>(items: T[]): Record<number, T>

  预期行为：
  - 接受带数字 id 的对象
  - 拒绝没有 id 的对象
  - 保留 T 上的其他字段
*/
function first<T>(items: T[]): T | undefined {
  return items[0];
}

function indexById<T extends { id: number }>(items: T[]): Record<number, T> {
  return items.reduce((acc, item) => {
    acc[item.id] = item;
    return acc;
  }, {} as Record<number, T>);
}

const firstTitle = first(["Hello, TypeScript!", "Second title"]);
const firstPostId = first([1, 2, 3]);

/*
  Part 4：观察编译期错误

  这些错误样例要保持注释状态。学习某个错误时：
  1. 临时取消这段块注释。
  2. 运行 `npm run check`。
  3. 阅读编译器报错。
  4. 做 Part 5 构建前，把注释恢复。

  const post: Post = {
    id: 1,
    userId: 1,
    title: "Hello, TypeScript!",
    body: "A type-safe way to model API objects.",
  };
  post.id = 2;

  const post1: Post = {
    id: 1,
    userId: 1,
    title: "Hello, TypeScript!",
  };

  const post2: PostCreate = {
    userId: 1,
    title: "Hello, TypeScript!",
    body: "A type-safe way to model API objects.",
  };
  indexById([post2]);
*/

const post: Post = {
  id: 1,
  userId: 1,
  title: "Hello, TypeScript!",
  body: "A type-safe way to model API objects.",
};

const postMap: PostMap = indexById([post]);

/*
  Part 5：运行时边界

  TODO：编译后查看生成的 JS，并回答：
  - 哪些类型声明消失了？
  - 哪些运行时代码保留下来了？
*/

/*
  Part 6：结构化类型

  目标：
  证明 TypeScript 主要检查对象结构，而不是类型名字。
*/
interface User {
  id: number;
  name: string;
  email: string;
}

interface Admin {
  id: number;
  name: string;
  email: string;
}

const user: User = {
  id: 1,
  name: "张三",
  email: "zhangsan@example.com",
};

const admin: Admin = user;

/*
  Part 7：unknown vs any 与 strict 下的可选字段

  目标：
  - 理解为什么外部数据应该先按 `unknown` 处理，而不是 `any`。
  - 练习在调用字符串方法前先处理 `undefined`。
*/
function safePrint(value: unknown): void {
  if (typeof value === "string") {
    console.log(value.toUpperCase());
  }
}

function unsafePrint(value: any): void {
  console.log(value.toUpperCase());
}

/*
  unsafePrint(123);
  编译器不会拦，因为 any 关闭了类型检查；
  但运行时 number 没有 toUpperCase，会报错。
*/

interface Test {
  body?: string;
}

function render(test: Test): string {
  if (test.body) {
    return test.body.toUpperCase();
  }

  return "EMPTY";
}

/*
  Part 8：配置对象的类型校验

  背景：
  真实前端项目里常有配置对象，例如菜单、路由、权限、请求配置。
  这类对象既要被 TypeScript 检查结构，又希望保留字面量信息。
*/
interface ConfigItem {
  key: string;
  label: string;
  enabled: boolean;
}

const configItem = {
  key: "feature",
  label: "新功能",
  enabled: true,
};

const configItem1: ConfigItem = {
  key: "feature",
  label: "新功能",
  enabled: true,
};

const configItem2 = {
  key: "feature",
  label: "新功能",
  enabled: true,
} satisfies ConfigItem;

const configItem3 = {
  key: "feature",
  label: "新功能",
  enabled: true,
  extra: "extra",
} as ConfigItem;

/*
  配置错误错题标本：

  const brokenConfig: ConfigItem = {
    key: 1,
    label: "新功能",
    extra: "extra",
  };

  这段同时包含：
  - key 字段类型错误：ConfigItem.key 需要 string。
  - enabled 必填字段缺失。
  - extra 多写了一个 ConfigItem 不需要的字段。
*/

/*
  Part 8 标准答案：

  1. `as` 不是严格检查类型，而是告诉编译器“信我”。

  `as ConfigItem` 本质是类型断言，更像对编译器说：
  “请把这个值当作 ConfigItem 使用，我知道自己在做什么。”

  普通类型标注和 `satisfies` 更像“请检查我是否满足这个结构”；
  `as` 更像“我断言它就是这个结构”。

  但 `as` 不是完全免死金牌。TypeScript 仍会做最低限度的合理性检查：
  如果源类型和目标类型差得太远，或者同名字段类型明显冲突，编译器仍可能报错。

  例如下面这种情况可能失败：

  const badConfig = {
    key: 1,
    label: "新功能",
    enabled: "yes",
  } as ConfigItem;

  原因是：
  - ConfigItem.key 需要 string，但这里是 number。
  - ConfigItem.enabled 需要 boolean，但这里是 string。
  - 这不是“少一两个字段”的问题，而是已有字段类型和目标类型明显冲突。

  如果强行绕过，通常要写成 `as unknown as ConfigItem`。
  但这几乎等于把类型系统关掉，真实项目里除非边界理由非常明确，否则不推荐。

  2. `satisfies` 更适合“要检查对象满足某个结构，但又想保留对象自身精确推断”的场景。

  普通类型标注：

  const config: ConfigItem = {
    key: "feature",
    label: "新功能",
    enabled: true,
  };

  这会把变量整体按 ConfigItem 看待。

  `satisfies`：

  const config = {
    key: "feature",
    label: "新功能",
    enabled: true,
  } satisfies ConfigItem;

  这会检查它满足 ConfigItem，同时尽量保留对象字面量自己的精确信息。

  3. 菜单、路由、权限配置适合用 `satisfies`，因为这类配置通常有两个要求：

  - 必须满足统一结构，比如 key、label、enabled 等字段不能乱。
  - 又希望保留每一项自己的精确信息，比如固定的 key 字面量，后续可用于权限判断、路由跳转或菜单匹配。

  所以配置对象常见选择是：
  - 不用 `as` 糊过去，因为它容易掩盖真实结构错误。
  - 不一定只用普通类型标注，因为它可能让字面量信息变宽。
  - 优先考虑 `satisfies`，既做结构校验，又保留对象本身的精确推断。
*/
