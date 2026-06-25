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
          <div className="todo-row" key={todo.id} onClick={() => onComplete(todo.id)}>
            <span className="todo-title">{todo.title}</span>
            <span className={`status-badge ${todo.completed ? "is-done" : "is-open"}`}>
              {todo.completed ? "已完成" : "进行中"}
            </span>
            <button
              className="delete-button"
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
