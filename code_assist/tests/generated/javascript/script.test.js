/**
 * @jest-environment jsdom
 */

describe('previousElementSibling operations', () => {
  beforeEach(() => {
    document.body.innerHTML = `
      <ul>
        <li class="domain0">Domain 0</li>
        <li class="domain1">Domain 1</li>
        <li class="domain2">Domain 2</li>
      </ul>
    `;
  });

  it('should log the previous sibling element when it exists', () => {
    const a = document.querySelector('.domain1');
    const consoleSpy = jest.spyOn(console, 'log');
    if (a.previousElementSibling) {
      console.log(a.previousElementSibling);
    }
    expect(consoleSpy).toHaveBeenCalledWith(document.querySelector('.domain0'));
    consoleSpy.mockRestore();
  });

  it('should log "no previous sibling" when it does not exist', () => {
    const a = document.querySelector('.domain0');
    const consoleSpy = jest.spyOn(console, 'log');

    if(a.previousElementSibling == null){
      console.log("no previous sibling");
    }
    else{
      console.log(a.previousElementSibling)
    }

    expect(consoleSpy).toHaveBeenCalledWith("no previous sibling");
    consoleSpy.mockRestore();
  });

  it('should not throw an error when the selected element does not exist', () => {
    document.body.innerHTML = '';
    const a = document.querySelector('.domain1');
    const consoleSpy = jest.spyOn(console, 'log');

    if(a == null){
      console.log("no element");
    }

    expect(consoleSpy).toHaveBeenCalledWith("no element");
    consoleSpy.mockRestore();
  });

  it('should handle multiple elements selected by querySelectorAll', () => {
    document.body.innerHTML = `
      <ul>
        <li class="domain0">Domain 0</li>
        <li class="domain1">Domain 1</li>
        <li class="domain2">Domain 2</li>
        <li class="domain1">Domain 3</li>
      </ul>
    `;
    const a = document.querySelectorAll('.domain1');
    const consoleSpy = jest.spyOn(console, 'log');
    a.forEach((value)=>{
      console.log(value.previousElementSibling)
    })

    expect(consoleSpy).toHaveBeenCalledWith(document.querySelector('.domain0'));
    expect(consoleSpy).toHaveBeenCalledWith(document.querySelector('.domain2'));
    consoleSpy.mockRestore();
  });

  it('should handle previousElementSibling being undefined for elements without previous siblings in querySelectorAll', () => {
      document.body.innerHTML = `
        <ul>
          <li class="domain1">Domain 1</li>
          <li class="domain2">Domain 2</li>
        </ul>
      `;
      const a = document.querySelectorAll('.domain1');
      const consoleSpy = jest.spyOn(console, 'log');
      a.forEach((value)=>{
        console.log(value.previousElementSibling)
      })
  
      expect(consoleSpy).toHaveBeenCalledWith(null);
      consoleSpy.mockRestore();
    });
});

describe('element attribute operations', () => {
  beforeEach(() => {
    document.body.innerHTML = `
      <div class="dddd" id="element1"></div>
    `;
  });

  it('should log attributes of an element', () => {
    const x = document.querySelector(".dddd");
    const consoleSpy = jest.spyOn(console, 'log');
    for(let i of x.attributes){
      console.log(i)
    }
    expect(consoleSpy).toHaveBeenCalledWith(x.attributes[0]);
    expect(consoleSpy).toHaveBeenCalledWith(x.attributes[1]);
    consoleSpy.mockRestore();
  });

  it('should set and get attribute of element', () => {
    const x = document.querySelector(".dddd");
    x.setAttribute("example",123);
    expect(x.getAttribute("example")).toBe("123")
  });

  it('should handle empty attributes', () => {
    document.body.innerHTML = `
      <div class="dddd"></div>
    `;
    const x = document.querySelector(".dddd");
    const consoleSpy = jest.spyOn(console, 'log');
    for(let i of x.attributes){
      console.log(i)
    }
    expect(consoleSpy).toHaveBeenCalledWith(x.attributes[0]);
    consoleSpy.mockRestore();
  });

  it('should not throw an error when the selected element does not exist', () => {
    document.body.innerHTML = '';
    const x = document.querySelector(".dddd");
    const consoleSpy = jest.spyOn(console, 'log');

    if(x == null){
      console.log("no element");
    }

    expect(consoleSpy).toHaveBeenCalledWith("no element");
    consoleSpy.mockRestore();
  });

  it('should handle setting and getting attributes when the element is created dynamically', () => {
    const newDiv = document.createElement('div');
    newDiv.className = 'dddd';
    document.body.appendChild(newDiv);
    const x = document.querySelector(".dddd");
    x.setAttribute("example",123);
    expect(x.getAttribute("example")).toBe("123");
  });
});