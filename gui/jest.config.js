module.exports = {
  testEnvironment: 'jsdom', // изменено с 'node' на 'jsdom' для поддержки DOM API
  testMatch: ['**/__tests__/**/*.[jt]s?(x)', '**/?(*.)+(spec|test).[tj]s?(x)'],
  transform: {
    '^.+\\.[tj]s$': 'babel-jest'
  }
};