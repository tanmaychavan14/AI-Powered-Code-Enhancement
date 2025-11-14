describe('multiply', () => {
    it('should multiply two positive numbers', () => {
        expect(multiply(2, 3)).toBe(6);
    });

    it('should multiply a positive and a negative number', () => {
        expect(multiply(2, -3)).toBe(-6);
    });

    it('should multiply two negative numbers', () => {
        expect(multiply(-2, -3)).toBe(6);
    });

    it('should multiply by zero', () => {
        expect(multiply(5, 0)).toBe(0);
    });

    it('should multiply zero by a number', () => {
        expect(multiply(0, 5)).toBe(0);
    });

    it('should multiply decimal numbers', () => {
        expect(multiply(2.5, 2)).toBe(5);
    });

    it('should throw an error if either argument is not a number', () => {
        expect(() => multiply('2', 3)).toThrow(TypeError);
        expect(() => multiply(2, '3')).toThrow(TypeError);
        expect(() => multiply(null, 3)).toThrow(TypeError);
        expect(() => multiply(undefined, 3)).toThrow(TypeError);
    });
});

describe('Calculator', () => {
    let calculator;

    beforeEach(() => {
        calculator = new Calculator();
    });

    describe('add', () => {
        it('should add two positive numbers', () => {
            expect(calculator.add(2, 3)).toBe(5);
        });

        it('should add a positive and a negative number', () => {
            expect(calculator.add(2, -3)).toBe(-1);
        });

        it('should add two negative numbers', () => {
            expect(calculator.add(-2, -3)).toBe(-5);
        });

        it('should add zero to a number', () => {
            expect(calculator.add(5, 0)).toBe(5);
        });

        it('should add two decimal numbers', () => {
            expect(calculator.add(2.5, 2.5)).toBe(5);
        });

        it('should throw an error if either argument is not a number', () => {
            expect(() => calculator.add('2', 3)).toThrow(TypeError);
            expect(() => calculator.add(2, '3')).toThrow(TypeError);
        });
    });

    describe('subtract', () => {
        it('should subtract two positive numbers', () => {
            expect(calculator.subtract(5, 3)).toBe(2);
        });

        it('should subtract a positive and a negative number', () => {
            expect(calculator.subtract(5, -3)).toBe(8);
        });

        it('should subtract two negative numbers', () => {
            expect(calculator.subtract(-5, -3)).toBe(-2);
        });

        it('should subtract zero from a number', () => {
            expect(calculator.subtract(5, 0)).toBe(5);
        });

         it('should subtract a number from zero', () => {
            expect(calculator.subtract(0, 5)).toBe(-5);
        });

        it('should subtract two decimal numbers', () => {
            expect(calculator.subtract(5.5, 2.5)).toBe(3);
        });

        it('should throw an error if either argument is not a number', () => {
            expect(() => calculator.subtract('5', 3)).toThrow(TypeError);
            expect(() => calculator.subtract(5, '3')).toThrow(TypeError);
        });
    });

    describe('square', () => {
        it('should square a positive number', () => {
            expect(calculator.square(4)).toBe(16);
        });

        it('should square a negative number', () => {
            expect(calculator.square(-4)).toBe(16);
        });

        it('should square zero', () => {
            expect(calculator.square(0)).toBe(0);
        });

        it('should square a decimal number', () => {
            expect(calculator.square(2.5)).toBe(6.25);
        });

        it('should throw an error if the argument is not a number', () => {
            expect(() => calculator.square('4')).toThrow(TypeError);
        });
    });
});