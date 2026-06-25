import { useState, useRef, useMemo, useEffect, type FormEvent } from "react";
import { TodoForm } from "./components/TodoForm";
import { TodoList } from "./components/TodoList";
import { TodoFilter } from "./components/TodoFilter";
import type { FilterMode, Todo } from "./types";
import { useLocalStorageTodos } from "./hooks/useLocalStorageTodos";

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
  const [todos, setTodos] = useLocalStorageTodos();
  const [draftTitle, setDraftTitle] = useState("");
  const [filter, setFilter] = useState<FilterMode>("all");
  const inputRef = useRef<HTMLInputElement | null>(null);

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
    inputRef.current?.focus();
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

  const visibleTodos = useMemo(
    () => getVisibleTodos(todos, filter),
    [todos, filter],
  );

  useEffect(() => {
    function handleKeyDown(event: KeyboardEvent): void {
      if (event.key !== "Escape") {
        return;
      }

      setDraftTitle("");
      inputRef.current?.focus();
    }

    window.addEventListener("keydown", handleKeyDown);

    return () => {
      window.removeEventListener("keydown", handleKeyDown);
    };
  }, []);

  return (
    <main className="app-shell">
      <section className="workspace">
        <header className="workspace-header">
          <p className="eyebrow">D11 React + TypeScript</p>
          <h1>待办练习</h1>
        </header>

        <TodoForm
          inputRef={inputRef}
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
