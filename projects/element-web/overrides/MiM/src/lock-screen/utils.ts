export const DEFAULT_ATTEMPTS = 3;

export function parseCode(hiddenCode: string): [string, number] {
    const parsed = atob(hiddenCode);
    if (!parsed) return ["", Infinity];
    const split = parsed.split(" ");
    return [split[0], Number(split[1])];
}

export function encodeCode(code: string, attempts: number = DEFAULT_ATTEMPTS) {
    const raw = `${code} ${attempts}`;
    return btoa(raw);
}
