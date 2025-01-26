
# Quick tips to use the library

The Intel DFP library can export it's functions with different signatures so
it's crucial to use the same compiler definitions for all compilation units

There're three definitions that affect signatures:
* `DECIMAL_CALL_BY_REFERENCE`
* `DECIMAL_GLOBAL_ROUNDING`
* `DECIMAL_GLOBAL_EXCEPTION_FLAGS`

For example, let's convert the following string to a decimal
``` c++
static constexpr auto NUMBER = "0.000000000001";
```

## Default (all zeros)
If all the aforementioned variables are unset, you must provide a rounding mode
and a pointer to a variable with exception flags when calling the most of the 
functions. The result (if any) is passing as a return variable.

``` c++
_IDEC_round rnd = /* set to one of BID_ROUNDING_* from bid_functions.h */;
_IDEC_flags exc_flags{};
BID_UINT64 out = bid64_from_string(const_cast<char *>(NUMBER), rnd, &exc_flags);
/* now check the `exc_flags` for the presence of BID_*_EXCEPTION */
```

## Call by reference
You can change signatures of the library functions so that everything must be
passed indirectly by setting `DECIMAL_CALL_BY_REFERENCE=1`
``` c++
_IDEC_round rnd = /* set to one of BID_ROUNDING_* from bid_functions.h */;
_IDEC_flags exc_flags{};
BID_UINT64 out{};
bid64_from_string(&out, const_cast<char *>(NUMBER), &rnd, &exc_flags);
/* now check the `exc_flags` for the presence of BID_*_EXCEPTION */
```

## Global variables (all definitions are set)
If you want to reduce the function signatures, you can pass the rounding mode
and the exception flags as a global (thread local, actually) variables.

When both `DECIMAL_GLOBAL_ROUNDING` and `DECIMAL_GLOBAL_EXCEPTION_FLAGS` are set
to one, the convertion function must be called like this:

``` c++
_IDEC_glbround = /* set to one of BID_ROUNDING_* from bid_functions.h */;
_IDEC_glbflags = 0;
BID_UINT64 out{};
bid64_from_string(&out, const_cast<char *>(NUMBER));
/* now check the `_IDEC_glbflags` for the presence of BID_*_EXCEPTION */
```


