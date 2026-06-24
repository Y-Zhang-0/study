import type { Todo } from "../types";

interface TodoListProps {
  todos: Todo[];
  onDelete: (id: number) => void;
  onComplete: (id: number) => void;
}

export function TodoList({ todos, onDelete, onComplete }: TodoListProps) {
  return (
    <section className="todo-panel">
      {todos.length === 0 ? (
        <p className="empty-state">暂无数据</p>
      ) : (
        todos.map((todo) => (
          <div key={todo.id} onClick={() => onComplete(todo.id)}>
            <span>{todo.title}</span>
            <span>{todo.completed ? "已完成" : "进行中"}</span>
            <button
              onClick={(event) => {
                event.stopPropagation();
                onDelete(todo.id);
              }}
            >
              删除
            </button>
          </div>
        ))
      )}
    </section>
  );
}
