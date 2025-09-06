/**
 * @jest-environment node
 */
import('pdf-merger-js').then((module) => {
  const PDFMerger = module.default;
  const { mergepdfs } = require('../mergepdf'); // Adjust the path as necessary
  const fs = require('fs');

  // Mock the PDFMerger class and its methods
  jest.mock('pdf-merger-js', () => {
    return jest.fn().mockImplementation(() => {
      return {
        add: jest.fn().mockResolvedValue(undefined),
        save: jest.fn().mockResolvedValue(undefined),
      };
    });
  });

  // Mock console.log and console.error
  console.log = jest.fn();
  console.error = jest.fn();

  describe('mergepdfs', () => {
    let mergerInstance;

    beforeEach(() => {
      // Create a new instance of the mocked PDFMerger before each test
      mergerInstance = new PDFMerger();
      console.log.mockClear();
      console.error.mockClear();
    });

    it('should merge two PDFs successfully', async () => {
      const p1 = 'pdf1.pdf';
      const p2 = 'pdf2.pdf';
      await mergepdfs(p1, p2);

      expect(mergerInstance.add).toHaveBeenCalledTimes(2);
      expect(mergerInstance.add).toHaveBeenCalledWith(p1);
      expect(mergerInstance.add).toHaveBeenCalledWith(p2);
      expect(mergerInstance.save).toHaveBeenCalledWith('public/merged.pdf');
      expect(console.log).toHaveBeenCalledWith('PDFs merged successfully.');
    });

    it('should handle an error during merging', async () => {
      const p1 = 'pdf1.pdf';
      const p2 = 'pdf2.pdf';

      // Mock the save method to reject
      mergerInstance.save.mockRejectedValue(new Error('Save failed'));

      await mergepdfs(p1, p2);

      expect(mergerInstance.add).toHaveBeenCalledTimes(2);
      expect(mergerInstance.add).toHaveBeenCalledWith(p1);
      expect(mergerInstance.add).toHaveBeenCalledWith(p2);
      expect(mergerInstance.save).toHaveBeenCalledWith('public/merged.pdf');
      expect(console.error).toHaveBeenCalledWith('Error while merging PDFs:', new Error('Save failed'));
    });

    it('should handle empty PDF paths', async () => {
        const p1 = '';
        const p2 = '';
        await mergepdfs(p1, p2);

        expect(mergerInstance.add).toHaveBeenCalledTimes(2);
        expect(mergerInstance.add).toHaveBeenCalledWith(p1);
        expect(mergerInstance.add).toHaveBeenCalledWith(p2);
        expect(mergerInstance.save).toHaveBeenCalledWith('public/merged.pdf');
        expect(console.log).toHaveBeenCalledWith('PDFs merged successfully.');
    });

      it('should handle null PDF paths', async () => {
          const p1 = null;
          const p2 = null;
          await mergepdfs(p1, p2);

          expect(mergerInstance.add).toHaveBeenCalledTimes(2);
          expect(mergerInstance.add).toHaveBeenCalledWith(p1);
          expect(mergerInstance.add).toHaveBeenCalledWith(p2);
          expect(mergerInstance.save).toHaveBeenCalledWith('public/merged.pdf');
          expect(console.log).toHaveBeenCalledWith('PDFs merged successfully.');
      });
  });
}).catch((error) => {
  console.error('Error while importing pdf-merger-js:', error);
});