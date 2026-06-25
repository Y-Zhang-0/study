import type { Ref, FormEvent } from "react";

interface TodoFormProps {
  inputRef: Ref<HTMLInputElement>;
  title: string;
  onTitleChange: (title: string) => void;
  onSubmit: (event: FormEvent<HTMLFormElement>) => void;
}

export function TodoForm({
  inputRef,
  title,
  onTitleChange,
  onSubmit,
}: TodoFormProps) {
  return (
    <form className="todo-form" onSubmit={onSubmit}>
      <input
        ref={inputRef}
        value={title}
        onChange={(event) => onTitleChange(event.target.value)}
        placeholder="输入新的待办"
        autoFocus
      />
      <button type="submit">新增</button>
    </form>
  );
}
