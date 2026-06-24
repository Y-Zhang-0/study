import { useState, type FormEvent } from "react";
import { TodoForm } from "./components/TodoForm";
import { TodoList } from "./components/TodoList";
import { TodoFilter } from "./components/TodoFilter";
import { initialTodos } from "./data";
import type { FilterMode, Todo } from "./types";

function getVisibleTodos(todos: Todo[], filter: FilterMode): Todo[] {
  switch (filter) {
    case "all":
      return todos;
    case "completed":
      return todos.filter((todo) => todo.completed);
    case "active":
      return todos.filter((todo) => !todo.completed);
  }
}

export default function App() {
  const [todos, setTodos] = useState<Todo[]>(initialTodos);
  const [draftTitle, setDraftTitle] = useState("");
  const [filter, setFilter] = useState<FilterMode>("all");

  function handleSubmit(event: FormEvent<HTMLFormElement>): void {
    event.preventDefault();

    const title = draftTitle.trim();
    if (title === "") {
      return;
    }
    setTodos((oldTodos) => [
      ...oldTodos,
      { id: Date.now(), title, completed: false },
    ]);
    setDraftTitle("");
  }

  function handleDelete(id: number): void {
    setTodos((oldTodos) => oldTodos.filter((todo) => todo.id !== id));
  }

  function handleComplete(id: number): void {
    setTodos((oldTodos) =>
      oldTodos.map((todo) => {
        if (todo.id === id) {
          return { ...todo, completed: !todo.completed };
        }
        return todo;
      }),
    );
  }

  const visibleTodos = getVisibleTodos(todos, filter);

  return (
    <main className="app-shell">
      <section className="workspace">
        <header className="workspace-header">
          <p className="eyebrow">D10 React + TypeScript</p>
          <h1>待办练习</h1>
        </header>

        <TodoForm
          title={draftTitle}
          onTitleChange={setDraftTitle}
          onSubmit={handleSubmit}
        />

        <TodoFilter filter={filter} onFilterChange={setFilter} />

        <TodoList
          todos={visibleTodos}
          onDelete={handleDelete}
          onComplete={handleComplete}
        />
      </section>
    </main>
  );
}
