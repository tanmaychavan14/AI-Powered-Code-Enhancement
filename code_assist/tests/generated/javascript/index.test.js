'use strict';

const balanced = require('./balanced');

describe('balanced(a, b, str)', () => {
  it('should return null when a or b are not found', () => {
    expect(balanced('(', ')', 'hello world')).toBe(null);
    expect(balanced('{', '}', 'hello world')).toBe(null);
  });

  it('should return the correct balanced object for simple cases', () => {
    const result = balanced('(', ')', 'hello (world) test');
    expect(result).toEqual({
      start: 6,
      end: 12,
      pre: 'hello ',
      body: 'world',
      post: ' test'
    });
  });

  it('should return the correct balanced object when a and b are regexes', () => {
    const result = balanced(/\(/, /\)/, 'hello (world) test');
    expect(result).toEqual({
      start: 6,
      end: 12,
      pre: 'hello ',
      body: 'world',
      post: ' test'
    });
  });

  it('should handle nested delimiters correctly', () => {
    const result = balanced('(', ')', 'a (b (c) d) e');
    expect(result).toEqual({
      start: 2,
      end: 10,
      pre: 'a ',
      body: 'b (c) d',
      post: ' e'
    });
  });

  it('should return a balanced object with empty body if delimiters are next to each other', () => {
    const result = balanced('(', ')', 'hello () test');
    expect(result).toEqual({
      start: 6,
      end: 7,
      pre: 'hello ',
      body: '',
      post: ' test'
    });
  });

  it('should work when start and end delimiters are the same', () => {
    const result = balanced('x', 'x', 'axbcxdefxghi');
    expect(result).toEqual({
      start: 1,
      end: 5,
      pre: 'a',
      body: 'bc',
      post: 'defxghi',
    });
  });
});

describe('maybeMatch(reg, str)', () => {
  it('should return the matched string when the regex matches', () => {
    expect(maybeMatch(/hello/, 'hello world')).toBe('hello');
    expect(maybeMatch(/\d+/, '12345')).toBe('12345');
  });

  it('should return null when the regex does not match', () => {
    expect(maybeMatch(/goodbye/, 'hello world')).toBe(null);
    expect(maybeMatch(/\D+/, '12345')).toBe(null);
  });

  it('should handle empty strings correctly', () => {
    expect(maybeMatch(/hello/, '')).toBe(null);
    expect(maybeMatch(/^$/, '')).toBe('');
  });

  it('should handle regex with global flag correctly', () => {
    expect(maybeMatch(/a/g, 'banana')).toBe('a');
  });
});

describe('range(a, b, str)', () => {
  it('should return null when a or b are not found', () => {
    expect(balanced.range('(', ')', 'hello world')).toBe(undefined);
    expect(balanced.range('{', '}', 'hello world')).toBe(undefined);
  });

  it('should return the correct range for simple cases', () => {
    const result = balanced.range('(', ')', 'hello (world) test');
    expect(result).toEqual([6, 12]);
  });

  it('should handle nested delimiters correctly', () => {
    const result = balanced.range('(', ')', 'a (b (c) d) e');
    expect(result).toEqual([2, 10]);
  });

  it('should return a range when delimiters are next to each other', () => {
    const result = balanced.range('(', ')', 'hello () test');
    expect(result).toEqual([6, 7]);
  });

  it('should work when start and end delimiters are the same', () => {
    const result = balanced.range('x', 'x', 'axbcxdefxghi');
    expect(result).toEqual([1, 5]);
  });

  it('should return undefined if the start delimiter is not found', () => {
    expect(balanced.range('start', 'end', 'no start here')).toBe(undefined);
  });

  it('should return undefined if the end delimiter is not found after the start delimiter', () => {
    expect(balanced.range('start', 'end', 'start here, no end')).toBe(undefined);
  });
});