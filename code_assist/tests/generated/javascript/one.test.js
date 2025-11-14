/**
 * Adds two numbers together.
 *
 * @param {number} a The first number.
 * @param {number} b The second number.
 * @returns {number} The sum of a and b.
 * @throws {TypeError} If either a or b is not a number.
 */
function add(a, b) {
    if (typeof a !== 'number' || typeof b !== 'number') {
        throw new TypeError('Both arguments must be numbers.');
    }
    return a + b;
}

/**
 * Subtracts one number from another.
 *
 * @param {number} a The number to subtract from.
 * @param {number} b The number to subtract.
 * @returns {number} The difference between a and b.
 * @throws {TypeError} If either a or b is not a number.
 */
function subtract(a, b) {
    if (typeof a !== 'number' || typeof b !== 'number') {
        throw new TypeError('Both arguments must be numbers.');
    }
    return a - b;
}

describe('add', () => {
    it('should add two positive numbers correctly', () => {
        expect(add(5, 3)).toBe(8);
        expect(add(10, 20)).toBe(30);
    });

    it('should add a positive and a negative number correctly', () => {
        expect(add(5, -3)).toBe(2);
        expect(add(-5, 3)).toBe(-2);
    });

    it('should add two negative numbers correctly', () => {
        expect(add(-5, -3)).toBe(-8);
    });

    it('should add zero to a number correctly', () => {
        expect(add(5, 0)).toBe(5);
        expect(add(0, 5)).toBe(5);
        expect(add(0, 0)).toBe(0);
    });

    it('should throw a TypeError if either argument is not a number', () => {
        expect(() => add('5', 3)).toThrow(TypeError);
        expect(() => add(5, '3')).toThrow(TypeError);
        expect(() => add(null, 3)).toThrow(TypeError);
        expect(() => add(5, undefined)).toThrow(TypeError);
    });

    it('should add floating point numbers correctly', () => {
        expect(add(1.5, 2.5)).toBe(4);
        expect(add(0.1, 0.2)).toBeCloseTo(0.3);
    });
});

describe('subtract', () => {
    it('should subtract two positive numbers correctly', () => {
        expect(subtract(5, 3)).toBe(2);
        expect(subtract(20, 10)).toBe(10);
    });

    it('should subtract a positive and a negative number correctly', () => {
        expect(subtract(5, -3)).toBe(8);
        expect(subtract(-5, 3)).toBe(-8);
    });

    it('should subtract two negative numbers correctly', () => {
        expect(subtract(-5, -3)).toBe(-2);
    });

    it('should subtract zero from a number correctly', () => {
        expect(subtract(5, 0)).toBe(5);
        expect(subtract(0, 5)).toBe(-5);
        expect(subtract(0, 0)).toBe(0);
    });

    it('should throw a TypeError if either argument is not a number', () => {
        expect(() => subtract('5', 3)).toThrow(TypeError);
        expect(() => subtract(5, '3')).toThrow(TypeError);
        expect(() => subtract(null, 3)).toThrow(TypeError);
        expect(() => subtract(5, undefined)).toThrow(TypeError);
    });

     it('should subtract floating point numbers correctly', () => {
        expect(subtract(2.5, 1.5)).toBe(1);
        expect(subtract(0.3, 0.1)).toBeCloseTo(0.2);
    });
});