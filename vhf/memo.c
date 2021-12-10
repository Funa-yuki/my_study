static PyObject *
builtin_compile_impl(PyObject *module, PyObject *source, PyObject *filename,
                     const char *mode, int flags, int dont_inherit,
                     int optimize, int feature_version)
/*[clinic end generated code: output=b0c09c84f116d3d7 input=40171fb92c1d580d]*/
{
    PyObject *source_copy;
    const char *str;
    int compile_mode = -1;
    int is_ast;
    int start[] = {Py_file_input, Py_eval_input, Py_single_input, Py_func_type_input};
    PyObject *result;

    PyCompilerFlags cf = _PyCompilerFlags_INIT;
    cf.cf_flags = flags | PyCF_SOURCE_IS_UTF8;
    if (feature_version >= 0 && (flags & PyCF_ONLY_AST)) {
        cf.cf_feature_version = feature_version;
    }

    if (flags &
        ~(PyCF_MASK | PyCF_MASK_OBSOLETE | PyCF_COMPILE_MASK))
    {
        PyErr_SetString(PyExc_ValueError,
                        "compile(): unrecognised flags");
        goto error;
    }
    /* XXX Warn if (supplied_flags & PyCF_MASK_OBSOLETE) != 0? */

    if (optimize < -1 || optimize > 2) {
        PyErr_SetString(PyExc_ValueError,
                        "compile(): invalid optimize value");
        goto error;
    }

    if (!dont_inherit) {
        PyEval_MergeCompilerFlags(&cf);
    }

    if (strcmp(mode, "exec") == 0)
        compile_mode = 0;
    else if (strcmp(mode, "eval") == 0)
        compile_mode = 1;
    else if (strcmp(mode, "single") == 0)
        compile_mode = 2;
    else if (strcmp(mode, "func_type") == 0) {
        if (!(flags & PyCF_ONLY_AST)) {
            PyErr_SetString(PyExc_ValueError,
                            "compile() mode 'func_type' requires flag PyCF_ONLY_AST");
            goto error;
        }
        compile_mode = 3;
    }
    else {
        const char *msg;
        if (flags & PyCF_ONLY_AST)
            msg = "compile() mode must be 'exec', 'eval', 'single' or 'func_type'";
        else
            msg = "compile() mode must be 'exec', 'eval' or 'single'";
        PyErr_SetString(PyExc_ValueError, msg);
        goto error;
    }

    is_ast = PyAST_Check(source);
    if (is_ast == -1)
        goto error;
    if (is_ast) {
        if (flags & PyCF_ONLY_AST) {
            Py_INCREF(source);
            result = source;
        }
        else {
            PyArena *arena;
            mod_ty mod;

            arena = _PyArena_New();
            if (arena == NULL)
                goto error;
            mod = PyAST_obj2mod(source, arena, compile_mode);
            if (mod == NULL || !_PyAST_Validate(mod)) {
                _PyArena_Free(arena);
                goto error;
            }
            result = (PyObject*)_PyAST_Compile(mod, filename,
                                               &cf, optimize, arena);
            _PyArena_Free(arena);
        }
        goto finally;
    }

    str = _Py_SourceAsString(source, "compile", "string, bytes or AST", &cf, &source_copy);
    if (str == NULL)
        goto error;

    result = Py_CompileStringObject(str, filename, start[compile_mode], &cf, optimize);

    Py_XDECREF(source_copy);
    goto finally;

error:
    result = NULL;
finally:
    Py_DECREF(filename);
    return result;
}
