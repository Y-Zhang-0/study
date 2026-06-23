export {};

/*
  D9：TypeScript 进阶与运行时边界

  今日主题：
  - 联合类型、交叉类型、字面量类型
  - 可辨识联合，也叫 discriminated union
  - 类型守卫与控制流收窄
  - unknown 外部数据安全解析

  学习规则：
  - 教学示范区可以直接运行，用来学机制。
  - 今日作业区由你亲手完成，不要使用 any。
  - 错误样例保持注释状态，需要观察编译器时报错时再临时打开。
*/

/*
  Part 1：教学示范，商品库存场景

  这段是完整示范，不是今日作业答案。
  你要观察的是 TypeScript 如何根据 if / switch 判断，自动把联合类型收窄成更具体的类型。
*/

type InventorySource = "warehouse" | "store";

interface BaseProduct {
  id: number;
  name: string;
  source: InventorySource;
}

interface WarehouseProduct extends BaseProduct {
  source: "warehouse";
  warehouseCode: string;
  stock: number;
}

interface StoreProduct extends BaseProduct {
  source: "store";
  storeName: string;
  shelf: string;
}

type Product = WarehouseProduct | StoreProduct;

function renderProduct(product: Product): string {
  switch (product.source) {
    case "warehouse":
      return `${product.name} 来自仓库 ${product.warehouseCode}，库存 ${product.stock}`;
    case "store":
      return `${product.name} 在门店 ${product.storeName}，货架 ${product.shelf}`;
  }
}

const demoProduct: Product = {
  id: 1,
  name: "键盘",
  source: "warehouse",
  warehouseCode: "WH-01",
  stock: 12,
};

console.log(renderProduct(demoProduct));

/*
  Part 2：教学示范，自定义类型守卫

  类型守卫的返回类型 `value is WarehouseProduct` 不是普通 boolean。
  它在告诉 TypeScript：如果这个函数返回 true，那么 value 可以被当成 WarehouseProduct 使用。
*/

function isWarehouseProduct(value: Product): value is WarehouseProduct {
  return value.source === "warehouse";
}

function renderStock(product: Product): string {
  if (isWarehouseProduct(product)) {
    return `${product.name} 库存数量：${product.stock}`;
  }

  return `${product.name} 是门店商品，按货架位置展示`;
}

console.log(renderStock(demoProduct));

/*
  Part 3：今日作业，笔记/待办请求状态建模

  你要亲手完成：
  1. 定义一个 Todo 类型，至少包含 id、title、completed。
  2. 定义请求状态联合类型：
     - idle：还没请求
     - loading：请求中
     - success：请求成功，携带 data
     - error：请求失败，携带 message
  3. 写 renderState(state)：
     - idle 返回“尚未加载”
     - loading 返回“加载中”
     - success 返回第一条数据标题；没有数据时返回“暂无数据”
     - error 返回错误信息

  要求：
  - 必须使用可辨识联合。
  - 必须使用 switch。
  - 不要使用 any。
*/

interface Todo {
  id: number;
  title: string;
  completed: boolean;
}

type AsyncState<T> = 
 | {status: "idle"}
 | {status: "loading"}
 | {status: "success", data: T}
 | {status: "refreshing", data: T}
 | {status: "error", message: string}

function assertNever(state: never): never {
  throw new Error(`未处理的状态：${JSON.stringify(state)}`);
}

type TodoListState = AsyncState<Todo[]>;

function renderState(state: TodoListState): string {
  switch(state.status) {
    case "idle":
      return "尚未加载";
    case "loading":
      return "加载中";
    case "success":
      return state.data.length > 0 ? state.data[0].title : "暂无数据";
    case "error":
      return state.message;
    case "refreshing":
      return `刷新中，当前 ${state.data.length} 条`;
    default:
      return assertNever(state);
  }
}
renderState({status: "refreshing", data: []});
renderState({status: "success", data: []});

/*
  Part 4：今日作业，unknown 外部数据安全解析

  背景：
  JSON.parse、接口返回值、localStorage 读出来的数据，本质上都不可信。
  TypeScript 的类型只在编译期工作，不能保证运行时数据真的长得对。

  你要亲手完成：
  1. 写 isTodo(value: unknown): value is Todo。
  2. 写 parseTodos(input: unknown): Todo[]。
  3. parseTodos 只接受数组，并且只保留合法 Todo。

  要求：
  - 不要使用 any。
  - 需要先判断 typeof value === "object"。
  - 需要处理 value === null。
  - 需要判断数组用 Array.isArray。
*/

function isTodo(value: unknown): value is Todo {
  if(typeof value !== "object" || value === null){
    return false;
  }
  const todo = value as Record<string, unknown>;
  return typeof todo.id === "number" && 
    typeof todo.title === "string" && 
    typeof todo.completed === "boolean";
} 

function parseTodos(input: unknown): Todo[] {
  if(!Array.isArray(input)){
    return [];
  }
  return input.filter(isTodo);
}
/*
  Part 5：今日作业，交叉类型组合业务对象

  你要亲手完成：
  1. 定义 Timestamped，包含 createdAt 和 updatedAt。
  2. 定义 Owned，包含 ownerId。
  3. 用交叉类型组合出 TodoRecord。
  4. 写一个 createTodoRecord 函数，把基础 Todo 补成 TodoRecord。

  目标：
  让你看到交叉类型不是“二选一”，而是把多个结构合并成一个更完整的结构。
*/

interface Timestamped {
  createdAt: Date;
  updatedAt: Date;
}

interface Owned {
  ownerId: number;
}

type TodoRecord = Todo & Timestamped & Owned;

function createTodoRecord(todo: Todo): TodoRecord {
  return {
    ...todo,
    createdAt: new Date(),
    updatedAt: new Date(),
    ownerId: 1,
  }
}
/*
  Part 6：错误样例观察区

  学习时可以临时取消下面块注释，然后运行：
  npm run check

  看完报错后要恢复注释，保证最终工程能通过检查。

  const brokenProduct: Product = {
    id: 2,
    name: "鼠标",
    source: "warehouse",
    storeName: "中关村店",
    shelf: "A-01",
  };

  const unsafeValue: unknown = "not an object";
  unsafeValue.toUpperCase();

*/

type Action<T> = 
 | {type: "start"}
 | {type: "success", data: T}
 | {type: "fail", message: string}
 | {type: "refresh"} 

function transition(state: TodoListState, action: Action<Todo[]>): TodoListState {
  switch(action.type) {
    case "start":
      return {status: "loading"};
    case "success":
      return {status: "success", data: action.data};
    case "fail":
      return {status: "error", message: action.message};
    case "refresh": {
      if("data" in state){
        return {status: "refreshing", data: state.data};
      }
      return {status: "loading"};
    }
    default:
      return assertNever(action);
  }
}
