import { initialTodos } from "../data";
import type { Todo } from "../types";
import { useLocalStorageState } from "./useLocalStorageState";

function isTodo(value: unknown): value is Todo {
  if (typeof value !== "object" || value === null) {
    return false;
  }

  const todo = value as Record<string, unknown>;

  return (
    typeof todo.id === "number" &&
    typeof todo.title === "string" &&
    typeof todo.completed === "boolean"
  );
}

function isTodos(value: unknown): value is Todo[] {
  return Array.isArray(value) && value.every(isTodo);
}

export function useLocalStorageTodos() {
  return useLocalStorageState<Todo[]>({
    key: "todos",
    initialValue: initialTodos,
    validate: isTodos,
  });
}
