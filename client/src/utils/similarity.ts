export function jacardSimilarity<T>(list1: T[], list2: T[]): number {
    const set1 = new Set(list1);
    const set2 = new Set(list2);
    const intersection = new Set([...set1].filter((x) => set2.has(x)));
    const union = new Set([...set1, ...set2]);
    return intersection.size / union.size;
}
