describe('multiply', () => {
  it('should multiply two positive numbers correctly', () => {
    expect(multiply(5, 3)).toBe(15);
  });

  it('should multiply a positive and a negative number correctly', () => {
    expect(multiply(5, -3)).toBe(-15);
  });

  it('should multiply two negative numbers correctly', () => {
    expect(multiply(-5, -3)).toBe(15);
  });

  it('should multiply a number by zero correctly', () => {
    expect(multiply(5, 0)).toBe(0);
  });

  it('should multiply zero by a number correctly', () => {
    expect(multiply(0, 5)).toBe(0);
  });
});

describe('Calculator', () => {
  let calculator;

  beforeEach(() => {
    calculator = new Calculator();
  });

  describe('add', () => {
    it('should add two positive numbers correctly', () => {
      expect(calculator.add(5, 3)).toBe(8);
    });

    it('should add a positive and a negative number correctly', () => {
      expect(calculator.add(5, -3)).toBe(2);
    });

    it('should add two negative numbers correctly', () => {
      expect(calculator.add(-5, -3)).toBe(-8);
    });

    it('should add a number to zero correctly', () => {
      expect(calculator.add(5, 0)).toBe(5);
    });
  });

  describe('subtract', () => {
    it('should subtract two positive numbers correctly', () => {
      expect(calculator.subtract(5, 3)).toBe(2);
    });

    it('should subtract a positive and a negative number correctly', () => {
      expect(calculator.subtract(5, -3)).toBe(8);
    });

    it('should subtract two negative numbers correctly', () => {
      expect(calculator.subtract(-5, -3)).toBe(-2);
    });

    it('should subtract a number from zero correctly', () => {
      expect(calculator.subtract(0, 5)).toBe(-5);
    });
  });

  describe('square', () => {
    it('should square a positive number correctly', () => {
      expect(calculator.square(4)).toBe(16);
    });

    it('should square a negative number correctly', () => {
      expect(calculator.square(-4)).toBe(16);
    });

    it('should square zero correctly', () => {
      expect(calculator.square(0)).toBe(0);
    });

    it('should square a decimal number correctly', () => {
      expect(calculator.square(2.5)).toBe(6.25);
    });
  });
});