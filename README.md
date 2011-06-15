conkeror-bookmarks
==================
Copyright (c) Björn Edström <be@bjrn.se> 2011.

The idea here is to make some kind of bookmark manager for conkeror (the web browser).

Currently, the code here just implements a command to conkeror,

`M-x list-bookmarks`

That will simply print all your bookmarks in a new buffer.

Installation
------------

Put `conkeror-bookmarks.py` somwhere in your path, and put the following in your `.conkerorrc`

    interactive("list-bookmarks",
        "List all bookmarks",
        function (I) {
            var data = "", error = "";
            var result = yield shell_command(
                "conkeror-bookmarks.py --html",
                $fds = [{ output: async_binary_string_writer("") },
                        { input: async_binary_reader(function (s) data+=s||"") },
                        { input: async_binary_reader(function (s) error+=s||"") }]);
            if (result != 0 || error != "")
                throw new interactive_error("status "+result+", "+error);
            var uri = "data:text/html;charset=utf-8;base64,"+btoa(data);
            browser_object_follow(I.buffer, OPEN_NEW_BUFFER, load_spec({ uri: uri }));
        });
