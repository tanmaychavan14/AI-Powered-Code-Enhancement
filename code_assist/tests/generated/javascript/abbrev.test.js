const abbrev = require('./abbrev.js');

describe('abbrev', () => {
  it('should return an empty object for an empty list', () => {
    expect(abbrev([])).toEqual({});
  });

  it('should correctly abbrev a list of strings', () => {
    expect(abbrev(['foo', 'foobar', 'fizz', 'buzz'])).toEqual({
      f: 'foo',
      fo: 'foo',
      foo: 'foo',
      foob: 'foobar',
      fooba: 'foobar',
      foobar: 'foobar',
      fi: 'fizz',
      fizz: 'fizz',
      b: 'buzz',
      bu: 'buzz',
      buz: 'buzz',
      buzz: 'buzz',
    });
  });

  it('should correctly abbrev a list with similar strings', () => {
    expect(abbrev(['a', 'ab', 'abc', 'abcd'])).toEqual({
      a: 'a',
      ab: 'ab',
      abc: 'abc',
      abcd: 'abcd',
    });
  });

  it('should handle numeric inputs by converting them to strings', () => {
    expect(abbrev([1, 12, 123])).toEqual({
      1: 1,
      12: 12,
      123: 123,
    });
  });

  it('should handle duplicate entries by ignoring them', () => {
    expect(abbrev(['foo', 'foo', 'bar'])).toEqual({
      b: 'bar',
      ba: 'bar',
      bar: 'bar',
      f: 'foo',
      fo: 'foo',
      foo: 'foo',
    });
  });

  it('should handle multiple arguments passed as separate parameters', () => {
    expect(abbrev('foo', 'foobar', 'fizz', 'buzz')).toEqual({
      f: 'foo',
      fo: 'foo',
      foo: 'foo',
      foob: 'foobar',
      fooba: 'foobar',
      foobar: 'foobar',
      fi: 'fizz',
      fizz: 'fizz',
      b: 'buzz',
      bu: 'buzz',
      buz: 'buzz',
      buzz: 'buzz',
    });
  });
});

describe('lexSort', () => {
  it('should return 0 if strings are equal', () => {
    expect(abbrev.abbrev.lexSort('abc', 'abc')).toBe(0);
  });

  it('should return 1 if the first string is greater than the second', () => {
    expect(abbrev.abbrev.lexSort('b', 'a')).toBe(1);
  });

  it('should return -1 if the first string is less than the second', () => {
    expect(abbrev.abbrev.lexSort('a', 'b')).toBe(-1);
  });
});

describe('monkeyPatch', () => {
  beforeEach(() => {
    delete Array.prototype.abbrev;
    delete Object.prototype.abbrev;
  });

  afterEach(() => {
    delete Array.prototype.abbrev;
    delete Object.prototype.abbrev;
  });

  it('should add abbrev to Array.prototype', () => {
    abbrev.monkeyPatch();
    expect([].abbrev).toBeDefined();
  });

  it('should add abbrev to Object.prototype', () => {
    abbrev.monkeyPatch();
    expect({}.abbrev).toBeDefined();
  });

  it('should correctly abbrev an array using the monkey-patched method', () => {
    abbrev.monkeyPatch();
    expect(['foo', 'foobar', 'fizz', 'buzz'].abbrev()).toEqual({
      f: 'foo',
      fo: 'foo',
      foo: 'foo',
      foob: 'foobar',
      fooba: 'foobar',
      foobar: 'foobar',
      fi: 'fizz',
      fizz: 'fizz',
      b: 'buzz',
      bu: 'buzz',
      buz: 'buzz',
      buzz: 'buzz',
    });
  });

  it('should correctly abbrev the keys of an object using the monkey-patched method', () => {
    abbrev.monkeyPatch();
    const obj = { foo: 1, foobar: 2, fizz: 3, buzz: 4 };
    expect(obj.abbrev()).toEqual({
      f: 'foo',
      fo: 'foo',
      foo: 'foo',
      foob: 'foobar',
      fooba: 'foobar',
      foobar: 'foobar',
      fi: 'fizz',
      fizz: 'fizz',
      b: 'buzz',
      bu: 'buzz',
      buz: 'buzz',
      buzz: 'buzz',
    });
  });
});