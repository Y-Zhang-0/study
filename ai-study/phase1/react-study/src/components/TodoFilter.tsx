import type { FilterMode } from "../types";

interface TodoFilterProps {
  filter: FilterMode;
  onFilterChange: (filter: FilterMode) => void;
}

export function TodoFilter({ filter, onFilterChange }: TodoFilterProps) {
  return (
    <div>
      <button
        className={filter === "all" ? "active" : ""}
        onClick={() => onFilterChange("all")}
      >
        全部
      </button>
      <button
        className={filter === "completed" ? "active" : ""}
        onClick={() => onFilterChange("completed")}
      >
        已完成
      </button>
      <button
        className={filter === "active" ? "active" : ""}
        onClick={() => onFilterChange("active")}
      >
        进行中
      </button>
    </div>
  );
}
