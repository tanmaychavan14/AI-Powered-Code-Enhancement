// Function 1: Check if a number is even or odd
function checkEvenOdd(num) {
    if (num % 2 === 0) {
        return "Even number";
    } else {
        return "Odd number";
    }
}

// Function 2: Find the maximum of two numbers
function findMax(a, b) {
    if (a > b) {
        return a;
    } else {
        return b;
    }
}

// Function 3: Check voting eligibility
function canVote(age) {
    if (age >= 18) {
        return "Eligible to vote";
    } else {
        return "Not eligible to vote";
    }
}

// Function 4: Calculate grade based on marks
function calculateGrade(marks) {
    if (marks >= 90) {
        return "A Grade";
    } else if (marks >= 75) {
        return "B Grade";
    } else if (marks >= 50) {
        return "C Grade";
    } else {
        return "Fail";
    }
}

// Function 5: Check login status
function loginStatus(isLoggedIn) {
    if (isLoggedIn) {
        return "User is logged in";
    } else {
        return "User is logged out";
    }
}

// ---- Jest Test Cases ----

describe('checkEvenOdd', () => {
    test('should return "Even number" for a positive even number', () => {
        expect(checkEvenOdd(4)).toBe("Even number");
    });

    test('should return "Odd number" for a positive odd number', () => {
        expect(checkEvenOdd(7)).toBe("Odd number");
    });

    test('should return "Even number" for zero', () => {
        expect(checkEvenOdd(0)).toBe("Even number");
    });

    test('should return "Even number" for a negative even number', () => {
        expect(checkEvenOdd(-2)).toBe("Even number");
    });

    test('should return "Odd number" for a negative odd number', () => {
        expect(checkEvenOdd(-5)).toBe("Odd number");
    });

    test('should return "Odd number" for a large odd number', () => {
        expect(checkEvenOdd(99999)).toBe("Odd number");
    });
});

describe('findMax', () => {
    test('should return the first number if it is greater', () => {
        expect(findMax(10, 5)).toBe(10);
    });

    test('should return the second number if it is greater', () => {
        expect(findMax(5, 10)).toBe(10);
    });

    test('should return either number if both are equal', () => {
        expect(findMax(7, 7)).toBe(7);
    });

    test('should handle negative numbers correctly (first is max)', () => {
        expect(findMax(-3, -10)).toBe(-3);
    });

    test('should handle negative numbers correctly (second is max)', () => {
        expect(findMax(-10, -3)).toBe(-3);
    });

    test('should handle zero and a positive number', () => {
        expect(findMax(0, 5)).toBe(5);
    });
});

describe('canVote', () => {
    test('should return "Eligible to vote" for age 18', () => {
        expect(canVote(18)).toBe("Eligible to vote");
    });

    test('should return "Eligible to vote" for age above 18', () => {
        expect(canVote(25)).toBe("Eligible to vote");
    });

    test('should return "Not eligible to vote" for age below 18', () => {
        expect(canVote(17)).toBe("Not eligible to vote");
    });

    test('should return "Not eligible to vote" for age much below 18', () => {
        expect(canVote(10)).toBe("Not eligible to vote");
    });

    test('should return "Eligible to vote" for a very old age', () => {
        expect(canVote(99)).toBe("Eligible to vote");
    });

    test('should return "Not eligible to vote" for age 0', () => {
        expect(canVote(0)).toBe("Not eligible to vote");
    });
});

describe('calculateGrade', () => {
    test('should return "A Grade" for marks 90 or above', () => {
        expect(calculateGrade(95)).toBe("A Grade");
        expect(calculateGrade(90)).toBe("A Grade");
    });

    test('should return "B Grade" for marks between 75 and 89', () => {
        expect(calculateGrade(80)).toBe("B Grade");
        expect(calculateGrade(75)).toBe("B Grade");
    });

    test('should return "C Grade" for marks between 50 and 74', () => {
        expect(calculateGrade(60)).toBe("C Grade");
        expect(calculateGrade(50)).toBe("C Grade");
    });

    test('should return "Fail" for marks below 50', () => {
        expect(calculateGrade(45)).toBe("Fail");
        expect(calculateGrade(0)).toBe("Fail");
    });

    test('should return "Fail" for marks just below 50', () => {
        expect(calculateGrade(49)).toBe("Fail");
    });

    test('should return "A Grade" for perfect marks', () => {
        expect(calculateGrade(100)).toBe("A Grade");
    });
});

describe('loginStatus', () => {
    test('should return "User is logged in" when isLoggedIn is true', () => {
        expect(loginStatus(true)).toBe("User is logged in");
    });

    test('should return "User is logged out" when isLoggedIn is false', () => {
        expect(loginStatus(false)).toBe("User is logged out");
    });

    test('should return "User is logged in" for a truthy value (e.g., non-empty string)', () => {
        expect(loginStatus("someUser")).toBe("User is logged in");
    });

    test('should return "User is logged out" for a falsy value (e.g., null)', () => {
        expect(loginStatus(null)).toBe("User is logged out");
    });

    test('should return "User is logged in" for a truthy value (e.g., 1)', () => {
        expect(loginStatus(1)).toBe("User is logged in");
    });

    test('should return "User is logged out" for a falsy value (e.g., undefined)', () => {
        expect(loginStatus(undefined)).toBe("User is logged out");
    });
});