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
    test('should return "Even number" for an even number', () => {
        expect(checkEvenOdd(4)).toBe("Even number");
    });

    test('should return "Odd number" for an odd number', () => {
        expect(checkEvenOdd(7)).toBe("Odd number");
    });

    test('should return "Even number" for zero', () => {
        expect(checkEvenOdd(0)).toBe("Even number");
    });

    test('should return "Even number" for a negative even number', () => {
        expect(checkEvenOdd(-6)).toBe("Even number");
    });

    test('should return "Odd number" for a negative odd number', () => {
        expect(checkEvenOdd(-11)).toBe("Odd number");
    });
});

describe('findMax', () => {
    test('should return the first number if it is greater', () => {
        expect(findMax(10, 5)).toBe(10);
    });

    test('should return the second number if it is greater', () => {
        expect(findMax(3, 8)).toBe(8);
    });

    test('should return either number if both are equal', () => {
        expect(findMax(7, 7)).toBe(7);
    });

    test('should handle negative numbers correctly', () => {
        expect(findMax(-5, -2)).toBe(-2);
    });

    test('should handle mixed positive and negative numbers', () => {
        expect(findMax(10, -20)).toBe(10);
    });
});

describe('canVote', () => {
    test('should return "Eligible to vote" for age 18', () => {
        expect(canVote(18)).toBe("Eligible to vote");
    });

    test('should return "Eligible to vote" for age greater than 18', () => {
        expect(canVote(25)).toBe("Eligible to vote");
    });

    test('should return "Not eligible to vote" for age less than 18', () => {
        expect(canVote(17)).toBe("Not eligible to vote");
    });

    test('should return "Not eligible to vote" for a very young age', () => {
        expect(canVote(5)).toBe("Not eligible to vote");
    });

    test('should handle zero age (not eligible)', () => {
        expect(canVote(0)).toBe("Not eligible to vote");
    });
});

describe('calculateGrade', () => {
    test('should return "A Grade" for marks 90 or above', () => {
        expect(calculateGrade(95)).toBe("A Grade");
        expect(calculateGrade(90)).toBe("A Grade");
    });

    test('should return "B Grade" for marks 75 to 89', () => {
        expect(calculateGrade(82)).toBe("B Grade");
        expect(calculateGrade(75)).toBe("B Grade");
        expect(calculateGrade(89)).toBe("B Grade");
    });

    test('should return "C Grade" for marks 50 to 74', () => {
        expect(calculateGrade(60)).toBe("C Grade");
        expect(calculateGrade(50)).toBe("C Grade");
        expect(calculateGrade(74)).toBe("C Grade");
    });

    test('should return "Fail" for marks below 50', () => {
        expect(calculateGrade(45)).toBe("Fail");
        expect(calculateGrade(0)).toBe("Fail");
        expect(calculateGrade(-10)).toBe("Fail"); // Assuming marks can be negative, though not typical
    });
});

describe('loginStatus', () => {
    test('should return "User is logged in" when isLoggedIn is true', () => {
        expect(loginStatus(true)).toBe("User is logged in");
    });

    test('should return "User is logged out" when isLoggedIn is false', () => {
        expect(loginStatus(false)).toBe("User is logged out");
    });

    // Additional tests for robustness, though the function is simple
    test('should return "User is logged in" for truthy values (e.g., non-empty string)', () => {
        // Based on the strict `if (isLoggedIn)` check, any truthy value behaves like true
        expect(loginStatus("someUser")).toBe("User is logged in");
    });

    test('should return "User is logged out" for falsy values (e.g., null)', () => {
        // Based on the strict `if (isLoggedIn)` check, any falsy value behaves like false
        expect(loginStatus(null)).toBe("User is logged out");
    });
});