import type { FormEvent } from "react";

interface TodoFormProps {
  title: string;
  onTitleChange: (title: string) => void;
  onSubmit: (event: FormEvent<HTMLFormElement>) => void;
}

export function TodoForm({ title, onTitleChange, onSubmit }: TodoFormProps) {
  return (
    <form className="todo-form" onSubmit={onSubmit}>
      <input
        value={title}
        onChange={(event) => onTitleChange(event.target.value)}
        placeholder="输入新的待办"
      />
      <button type="submit">新增</button>
    </form>
  );
}
