/** @type {import('jest').Config} */
const config = {
  testEnvironment:       "jsdom",
  setupFilesAfterEnv:    ["<rootDir>/jest.setup.ts"],
  moduleNameMapper: {
    "^@/(.*)$": "<rootDir>/$1",
  },
  transform: {
    "^.+\\.(ts|tsx)$": ["ts-jest", {
      tsconfig: {
        jsx: "react-jsx",
      },
    }],
  },
  testMatch: ["**/__tests__/**/*.test.(ts|tsx)"],
};

module.exports = config;