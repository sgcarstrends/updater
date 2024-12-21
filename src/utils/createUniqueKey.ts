export const createUniqueKey = (
  record: Record<string, any>,
  keyFields: string[],
) => keyFields.map((field) => record[field]).join("-");
