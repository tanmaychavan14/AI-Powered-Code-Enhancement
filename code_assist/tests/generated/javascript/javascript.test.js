describe('multiply', () => {
    it('should multiply two positive numbers correctly', () => {
        expect(multiply(2, 3)).toBe(6);
    });

    it('should multiply a positive and a negative number correctly', () => {
        expect(multiply(2, -3)).toBe(-6);
    });

    it('should multiply two negative numbers correctly', () => {
        expect(multiply(-2, -3)).toBe(6);
    });

    it('should multiply by zero correctly', () => {
        expect(multiply(5, 0)).toBe(0);
    });

    it('should multiply decimal numbers correctly', () => {
        expect(multiply(2.5, 2)).toBe(5);
    });
});

describe('Calculator', () => {
    let calculator;

    beforeEach(() => {
        calculator = new Calculator();
    });

    it('should add two numbers correctly', () => {
        expect(calculator.add(1, 2)).toBe(3);
    });

    it('should subtract two numbers correctly', () => {
        expect(calculator.subtract(5, 3)).toBe(2);
    });

    it('should square a number correctly', () => {
        expect(calculator.square(4)).toBe(16);
    });
});