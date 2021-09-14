#define PY_SSIZE_T_CLEAN
#include <Python.h>

#ifndef SCRIPT
    #define SCRIPT "/usr/local/bin/pyautosplit"
#endif

// https://docs.python.org/3/extending/embedding.html
int main(int argc, char *argv[])
{
    // Python requires wide chars
    int wargc = argc + 1;
    wchar_t *wargv[wargc];

    // replace this wrapper with the PyAutoSplit
    wargv[0] = Py_DecodeLocale(SCRIPT, NULL);
    wargv[1] = Py_DecodeLocale("--from-wrapper", NULL);
    if(wargv[0] == NULL || wargv[1] == NULL)
    {
        return EXIT_FAILURE;
    }

    // convert remaining arguments to wide chars
    for (int i = 1; i < argc; i++)
    {
        wargv[i+1] = Py_DecodeLocale(argv[i], NULL);
        if(wargv[i+1] == NULL)
        {
            return EXIT_FAILURE;
        }
    }

    // initialize embedded python interpreter
    Py_SetProgramName(wargv[0]);
    Py_Initialize();
    PySys_SetArgv(wargc, wargv);

    // open and run PyAutoSplit with embedded
    // Python interpreter
    FILE *file = fopen(SCRIPT, "r");
    PyRun_SimpleFile(file, "pyautosplit");

    // cleanup
    if (Py_FinalizeEx() < 0)
    {
        exit(120);
    }

    PyMem_RawFree(wargv[0]);

    return 0;
}
