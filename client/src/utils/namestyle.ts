export const snakeToCamelCase = (snakeStr: string): string => {
    return snakeStr.replace(/(_\w)/g, match => match[1].toUpperCase());
}

const camelCaseDict = (data: object): object => {
    return Object.fromEntries(
        Object
            .entries(data)
            .map(([key, value]) => [snakeToCamelCase(key), value])
    )
}

export const CamelCaseList = (data: object[]): object[] => {
    return data.map(item => camelCaseDict(item))
}
