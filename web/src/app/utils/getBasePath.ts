export default function getBasePath(role: string) : string{
    const pathMap = new Map([
        ['admin','admin'],
        ['manager','admin'],
        ['staff','sumula'],
        ['player','profile']
    ]);

    return pathMap.get(role) || "contests";
}