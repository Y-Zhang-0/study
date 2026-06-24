export interface Todo {
  id: number;
  title: string;
  completed: boolean;
}

export type FilterMode = "all" | "active" | "completed";
