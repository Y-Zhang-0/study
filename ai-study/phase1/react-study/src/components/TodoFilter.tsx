import type { FilterMode } from "../types";

interface TodoFilterProps {
  filter: FilterMode;
  onFilterChange: (filter: FilterMode) => void;
}

export function TodoFilter({ filter, onFilterChange }: TodoFilterProps) {
  return (
    <div className="todo-filter">
      <button
        type="button"
        className={`filter-button ${filter === "all" ? "is-active" : ""}`}
        aria-pressed={filter === "all"}
        onClick={() => onFilterChange("all")}
      >
        全部
      </button>
      <button
        type="button"
        className={`filter-button ${filter === "completed" ? "is-active" : ""}`}
        aria-pressed={filter === "completed"}
        onClick={() => onFilterChange("completed")}
      >
        已完成
      </button>
      <button
        type="button"
        className={`filter-button ${filter === "active" ? "is-active" : ""}`}
        aria-pressed={filter === "active"}
        onClick={() => onFilterChange("active")}
      >
        进行中
      </button>
    </div>
  );
}
