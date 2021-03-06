# Copyright (C) 2020 FireEye, Inc. All Rights Reserved.

from .. import api


class Shell32(api.ApiHandler):

    """
    Implements exported functions from shell32.dll
    """

    name = 'shell32'
    apihook = api.ApiHandler.apihook
    impdata = api.ApiHandler.impdata

    def __init__(self, emu):

        super(Shell32, self).__init__(emu)

        self.funcs = {}
        self.data = {}
        self.window_hooks = {}
        self.handle = 0
        self.win = None

        super(Shell32, self).__get_hook_attrs__(self)

    @apihook('SHCreateDirectoryEx', argc=3)
    def SHCreateDirectoryEx(self, emu, argv, ctx={}):
        '''
        int SHCreateDirectoryExA(
            HWND                      hwnd,
            LPCSTR                    pszPath,
            const SECURITY_ATTRIBUTES *psa
        );
        '''

        hwnd, pszPath, psa = argv

        cw = self.get_char_width(ctx)
        dn = ''
        if pszPath:
            dn = self.read_mem_string(pszPath, cw)
            argv[1] = dn

            self.log_file_access(dn, 'directory_create')

        return 0

    @apihook('ShellExecute', argc=6)
    def ShellExecute(self, emu, argv, ctx={}):
        '''
        HINSTANCE ShellExecuteA(
            HWND   hwnd,
            LPCSTR lpOperation,
            LPCSTR lpFile,
            LPCSTR lpParameters,
            LPCSTR lpDirectory,
            INT    nShowCmd
        );
        '''

        hwnd, lpOperation, lpFile, lpParameters, lpDirectory, nShowCmd = argv

        cw = self.get_char_width(ctx)

        fn = ''
        param = ''
        dn = ''
        if lpOperation:
            op = self.read_mem_string(lpOperation, cw)
            argv[1] = op
        if lpFile:
            fn = self.read_mem_string(lpFile, cw)
            argv[2] = fn
        if lpParameters:
            param = self.read_mem_string(lpParameters, cw)
            argv[3] = param
        if lpDirectory:
            dn = self.read_mem_string(lpDirectory, cw)
            argv[4] = dn

        if dn and fn:
            fn = '%s\\%s' % (dn, fn)

        proc = emu.create_process(path=fn, cmdline=param)
        self.log_process_event(proc, 'create')

        return 33

    @apihook('IsUserAnAdmin', argc=0)
    def IsUserAnAdmin(self, emu, argv, ctx={}):
        """
        BOOL IsUserAnAdmin();
        """
        return emu.get_user().get('is_admin', False)
