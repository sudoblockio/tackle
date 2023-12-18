- Finish off initial key macros
- Update `dict_hook_macro_hook_key`
  - Issue is if we have any logic (ie flags) we can't assert them properly
    - ie
      - <-:
          # This should return an empty string?
          a_try->: yaml does-no-exist --try
    - This isn't possible - it is an edge case so perhaps catch it later?
    - The context is also not passed between fields
      - So