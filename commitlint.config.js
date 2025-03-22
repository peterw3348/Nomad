module.exports = {
  extends: ['@commitlint/config-conventional'],
  rules: {
    'header-max-length': [2, 'always', 72],  // Enforce max 72 characters
    'type-enum': [
      2,
      'always',
      ['bump','feat', 'fix', 'docs', 'style', 'refactor', 'test', 'chore', 'ci', 'release']
    ],  // Allowed commit types
    'subject-case': [2, 'always', ['sentence-case', 'lower-case']],
  },
};
