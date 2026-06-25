import { useEffect, useState, type Dispatch, type SetStateAction } from "react";

interface UseLocalStorageStateOptions<T> {
  key: string;
  initialValue: T;
  validate: (value: unknown) => value is T;
}

type UseLocalStorageStateResult<T> = readonly [
  T,
  Dispatch<SetStateAction<T>>,
];

export function useLocalStorageState<T>({
  key,
  initialValue,
  validate,
}: UseLocalStorageStateOptions<T>): UseLocalStorageStateResult<T> {
  const [state, setState] = useState<T>(() => {
    const rawValue = localStorage.getItem(key);

    if (rawValue === null) {
      return initialValue;
    }

    try {
      const parsedValue: unknown = JSON.parse(rawValue);
      return validate(parsedValue) ? parsedValue : initialValue;
    } catch {
      return initialValue;
    }
  });

  useEffect(() => {
    localStorage.setItem(key, JSON.stringify(state));
  }, [key, state]);

  return [state, setState] as const;
}
