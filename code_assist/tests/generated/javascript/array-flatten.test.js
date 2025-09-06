'use strict'

const arrayFlatten = require('./index') // Assuming the code is in index.js

describe('arrayFlatten', () => {
  describe('flattenWithDepth', () => {
    it('should flatten an array with a specified depth', () => {
      const array = [1, [2, [3, [4]], 5], 6]
      const result = arrayFlatten.__get__('flattenWithDepth')(array, [], 2) // Using __get__ to access the internal function
      expect(result).toEqual([1, 2, [3, [4]], 5, 6])
    })

    it('should flatten an array with a depth of 0', () => {
      const array = [1, [2, [3, [4]], 5], 6]
      const result = arrayFlatten.__get__('flattenWithDepth')(array, [], 0)
      expect(result).toEqual([1, [2, [3, [4]], 5], 6])
    })

    it('should handle an empty array', () => {
      const array = []
      const result = arrayFlatten.__get__('flattenWithDepth')(array, [], 2)
      expect(result).toEqual([])
    })

    it('should handle a depth greater than the nesting level', () => {
      const array = [1, [2, [3]]]
      const result = arrayFlatten.__get__('flattenWithDepth')(array, [], 5)
      expect(result).toEqual([1, 2, 3])
    })

    it('should handle an array with no nested arrays', () => {
      const array = [1, 2, 3]
      const result = arrayFlatten.__get__('flattenWithDepth')(array, [], 2)
      expect(result).toEqual([1, 2, 3])
    })
  })

  describe('flattenForever', () => {
    it('should flatten an array infinitely', () => {
      const array = [1, [2, [3, [4]], 5], 6]
      const result = arrayFlatten.__get__('flattenForever')(array, []) // Access internal function
      expect(result).toEqual([1, 2, 3, 4, 5, 6])
    })

    it('should handle an empty array', () => {
      const array = []
      const result = arrayFlatten.__get__('flattenForever')(array, [])
      expect(result).toEqual([])
    })

    it('should handle an array with no nested arrays', () => {
      const array = [1, 2, 3]
      const result = arrayFlatten.__get__('flattenForever')(array, [])
      expect(result).toEqual([1, 2, 3])
    })

    it('should handle an array with empty nested arrays', () => {
      const array = [1, [], [2, []], 3]
      const result = arrayFlatten.__get__('flattenForever')(array, [])
      expect(result).toEqual([1, 2, 3])
    })

    it('should handle an array with different data types', () => {
      const array = [1, [2, 'hello', [true]], 3]
      const result = arrayFlatten.__get__('flattenForever')(array, [])
      expect(result).toEqual([1, 2, 'hello', true, 3])
    })
  })

  describe('arrayFlatten', () => {
    it('should flatten an array infinitely when depth is not specified', () => {
      const array = [1, [2, [3, [4]], 5], 6]
      const result = arrayFlatten(array)
      expect(result).toEqual([1, 2, 3, 4, 5, 6])
    })

    it('should flatten an array with a specified depth', () => {
      const array = [1, [2, [3, [4]], 5], 6]
      const result = arrayFlatten(array, 2)
      expect(result).toEqual([1, 2, [3, [4]], 5, 6])
    })

    it('should handle an empty array', () => {
      const array = []
      const result = arrayFlatten(array)
      expect(result).toEqual([])
    })

    it('should handle an array with no nested arrays', () => {
      const array = [1, 2, 3]
      const result = arrayFlatten(array)
      expect(result).toEqual([1, 2, 3])
    })

    it('should handle a null depth', () => {
      const array = [1, [2, [3]]]
      const result = arrayFlatten(array, null);
      expect(result).toEqual([1, 2, 3]);
    });

    it('should handle undefined depth', () => {
      const array = [1, [2, [3]]]
      const result = arrayFlatten(array, undefined);
      expect(result).toEqual([1, 2, 3]);
    });

    it('should handle zero depth', () => {
        const array = [1, [2, [3]]]
        const result = arrayFlatten(array, 0);
        expect(result).toEqual([1, [2, [3]]]);
    });
  })
})