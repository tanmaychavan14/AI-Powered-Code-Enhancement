// Jest mock for axios. This directive must be at the top of the file
// to effectively mock the 'axios' module for any 'require("axios")' calls that follow.
jest.mock('axios');

// Original axios import.
// Due to 'jest.mock('axios')' above, this 'require' statement will
// now load the mocked version of axios, not the actual library.
const axios = require("axios");

// Original function implementation.
// The 'module.exports' statement is omitted as per the 'self-contained file'
// requirement, making 'fetchUser' directly accessible in the test scope.
async function fetchUser() {
    const response = await axios.get("https://jsonplaceholder.typicode.com/users/1");
    return response.data.name;
}

// Jest test cases for fetchUser()
describe('fetchUser', () => {
    // Define a standard mock user data structure for successful API responses.
    const mockUserData = {
        data: {
            name: "Leanne Graham",
            username: "Bret",
            email: "Sincere@april.biz",
            address: {
                street: "Kulas Light",
                suite: "Apt. 556",
                city: "Gwenborough",
                zipcode: "92998-3874",
                geo: { lat: "-37.3159", lng: "81.1496" }
            },
            phone: "1-770-736-8031 x56442",
            website: "hildegard.org",
            company: {
                name: "Romaguera-Crona",
                catchPhrase: "Multi-layered client-server neural-net",
                bs: "harness real-time e-markets"
            }
        }
    };

    // Before each test, clear all mock calls and reset mock implementations.
    // This ensures that each test runs in a clean, isolated environment.
    beforeEach(() => {
        axios.get.mockClear(); // Clears all calls to axios.get
    });

    // Test Case 1: Successfully fetches user name from a valid API response.
    test('should return the user name when the API call is successful and data is valid', async () => {
        // Arrange: Configure axios.get to resolve with our mock user data.
        axios.get.mockResolvedValueOnce(mockUserData);

        // Act: Call the function under test.
        const result = await fetchUser();

        // Assert: Verify the returned value and that axios.get was called correctly.
        expect(result).toBe("Leanne Graham");
        expect(axios.get).toHaveBeenCalledTimes(1);
        expect(axios.get).toHaveBeenCalledWith("https://jsonplaceholder.typicode.com/users/1");
    });

    // Test Case 2: Handles errors when the API call itself fails (e.g., network error).
    test('should throw an error if the API call fails (e.g., network issue)', async () => {
        // Arrange: Configure axios.get to reject with an error.
        const errorMessage = 'Network Error: Request failed';
        axios.get.mockRejectedValueOnce(new Error(errorMessage));

        // Act & Assert: Expect the function to throw the error.
        await expect(fetchUser()).rejects.toThrow(errorMessage);
        expect(axios.get).toHaveBeenCalledTimes(1);
        expect(axios.get).toHaveBeenCalledWith("https://jsonplaceholder.typicode.com/users/1");
    });

    // Test Case 3: Handles API responses that are missing the 'data' property.
    test('should throw a TypeError if the API response object lacks a "data" property', async () => {
        // Arrange: Mock an API response without the 'data' property.
        const mockResponseNoData = { status: 200, headers: { 'content-type': 'application/json' } };
        axios.get.mockResolvedValueOnce(mockResponseNoData);

        // Act & Assert: Expect a TypeError when trying to access 'undefined.name'.
        await expect(fetchUser()).rejects.toThrow(TypeError);
        await expect(fetchUser()).rejects.toThrow("Cannot read properties of undefined (reading 'name')");
        expect(axios.get).toHaveBeenCalledTimes(1);
        expect(axios.get).toHaveBeenCalledWith("https://jsonplaceholder.typicode.com/users/1");
    });

    // Test Case 4: Handles API responses where the 'data' property is explicitly null.
    test('should throw a TypeError if the "data" property in the response is null', async () => {
        // Arrange: Mock an API response where 'data' is null.
        const mockResponseNullData = { data: null };
        axios.get.mockResolvedValueOnce(mockResponseNullData);

        // Act & Assert: Expect a TypeError when trying to access 'null.name'.
        await expect(fetchUser()).rejects.toThrow(TypeError);
        await expect(fetchUser()).rejects.toThrow("Cannot read properties of null (reading 'name')");
        expect(axios.get).toHaveBeenCalledTimes(1);
        expect(axios.get).toHaveBeenCalledWith("https://jsonplaceholder.typicode.com/users/1");
    });

    // Test Case 5: Handles API responses where the 'name' property is missing from 'response.data'.
    test('should return undefined if the "name" property is not found in response.data', async () => {
        // Arrange: Mock an API response where 'data' is an object but 'name' is missing.
        const mockDataWithoutName = { data: { id: 1, username: "Bret", email: "test@example.com" } };
        axios.get.mockResolvedValueOnce(mockDataWithoutName);

        // Act: Call the function.
        const result = await fetchUser();

        // Assert: Expect the function to return undefined, as `response.data.name` would be undefined.
        expect(result).toBeUndefined();
        expect(axios.get).toHaveBeenCalledTimes(1);
        expect(axios.get).toHaveBeenCalledWith("https://jsonplaceholder.typicode.com/users/1");
    });

    // Test Case 6: Handles API responses where the 'data' property is a non-object primitive (e.g., a string).
    test('should throw a TypeError if the "data" property in response is a non-object primitive', async () => {
        // Arrange: Mock an API response where 'data' is a string.
        const mockResponsePrimitiveData = { data: "This is not an object" };
        axios.get.mockResolvedValueOnce(mockResponsePrimitiveData);

        // Act & Assert: Expect a TypeError when trying to access '.name' on a string primitive.
        await expect(fetchUser()).rejects.toThrow(TypeError);
        await expect(fetchUser()).rejects.toThrow("Cannot read properties of string (reading 'name')");
        expect(axios.get).toHaveBeenCalledTimes(1);
        expect(axios.get).toHaveBeenCalledWith("https://jsonplaceholder.typicode.com/users/1");
    });
});