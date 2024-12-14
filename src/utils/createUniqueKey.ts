export const createUniqueKey = (
  item: Record<string, any>,
  keyFields: string[],
) => keyFields.map((field) => item[field]).join("-");
