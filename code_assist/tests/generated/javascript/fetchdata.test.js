// For Jest to properly mock the 'axios' module, we declare it at the top of the test file.
// This ensures that when the copied code below calls `require("axios")`, it receives our mock
// instead of the real axios library, preventing actual network requests during tests.
jest.mock('axios', () => ({
  get: jest.fn(), // Mock the .get method of axios
}));

// --- Start of Function Implementations (Copied Verbatim) ---
const axios = require("axios"); // This will now resolve to the mocked axios object.

async function fetchUser() {
    const response = await axios.get("https://jsonplaceholder.typicode.com/users/1");
    return response.data.name;
}

module.exports = { fetchUser };
// --- End of Function Implementations ---


// --- Start of Jest Test Cases ---
describe('fetchUser', () => {
    // Before each test, we clear any previous mock calls and reset mock implementations.
    // This ensures that tests are isolated and do not affect each other's mock states.
    beforeEach(() => {
        axios.get.mockClear(); // Clears information about calls to the mock function
    });

    // Test Case 1: Verifies that fetchUser returns the correct user name on a successful API call.
    test('should return the name of the user on a successful API call', async () => {
        // Arrange: Define the mock response data for a successful API call.
        const mockUserData = {
            id: 1,
            name: 'Leanne Graham',
            username: 'Bret',
            email: 'Sincere@april.biz',
            address: { street: 'Kulas Light', suite: 'Apt. 556' },
            phone: '1-770-736-8031 x56442',
            website: 'hildegard.org',
            company: { name: 'Romaguera-Crona' },
        };
        // Set the mock implementation for axios.get to resolve with our mock data.
        axios.get.mockResolvedValue({ data: mockUserData });

        // Act: Call the function under test.
        const result = await fetchUser();

        // Assert: Verify the function's output and that axios.get was called correctly.
        expect(result).toBe('Leanne Graham');
        expect(axios.get).toHaveBeenCalledTimes(1);
        expect(axios.get).toHaveBeenCalledWith('https://jsonplaceholder.typicode.com/users/1');
    });

    // Test Case 2: Checks if fetchUser handles different valid user data correctly.
    test('should correctly extract name for different user data', async () => {
        // Arrange: Define mock data for a different user.
        const mockUserData = {
            id: 2,
            name: 'Ervin Howell',
            username: 'Antonette',
            email: 'Shanna@melissa.tv',
        };
        axios.get.mockResolvedValue({ data: mockUserData });

        // Act
        const result = await fetchUser();

        // Assert
        expect(result).toBe('Ervin Howell');
        expect(axios.get).toHaveBeenCalledTimes(1);
        expect(axios.get).toHaveBeenCalledWith('https://jsonplaceholder.typicode.com/users/1');
    });

    // Test Case 3: Ensures fetchUser correctly propagates errors when the API call fails.
    test('should throw an error if the API call fails', async () => {
        // Arrange: Set the mock to reject with an error, simulating a network or server error.
        const errorMessage = 'Network Error: Request failed with status code 500';
        axios.get.mockRejectedValue(new Error(errorMessage));

        // Act & Assert: Expect the function to throw the specified error.
        await expect(fetchUser()).rejects.toThrow(errorMessage);
        expect(axios.get).toHaveBeenCalledTimes(1);
        expect(axios.get).toHaveBeenCalledWith('https://jsonplaceholder.typicode.com/users/1');
    });

    // Test Case 4: Handles scenarios where the API response data is missing the 'name' property.
    test('should throw an error if the response data is missing the name property', async () => {
        // Arrange: Mock a response where 'data' exists, but the 'name' property is absent.
        const mockUserDataWithoutName = {
            id: 1,
            username: 'Bret',
            email: 'Sincere@april.biz',
        };
        axios.get.mockResolvedValue({ data: mockUserDataWithoutName });

        // Act & Assert: Expect a TypeError because `response.data.name` would be `undefined`.
        await expect(fetchUser()).rejects.toThrow(TypeError);
        await expect(fetchUser()).rejects.toThrow("Cannot read properties of undefined (reading 'name')");
        expect(axios.get).toHaveBeenCalledTimes(1);
        expect(axios.get).toHaveBeenCalledWith('https://jsonplaceholder.typicode.com/users/1');
    });

    // Test Case 5: Handles scenarios where the API returns null for the data property.
    test('should throw an error if the API returns null data', async () => {
        // Arrange: Mock a response where the entire 'data' property is null.
        axios.get.mockResolvedValue({ data: null });

        // Act & Assert: Expect a TypeError because `response.data` would be null.
        await expect(fetchUser()).rejects.toThrow(TypeError);
        await expect(fetchUser()).rejects.toThrow("Cannot read properties of null (reading 'name')");
        expect(axios.get).toHaveBeenCalledTimes(1);
        expect(axios.get).toHaveBeenCalledWith('https://jsonplaceholder.typicode.com/users/1');
    });
});
// --- End of Jest Test Cases ---