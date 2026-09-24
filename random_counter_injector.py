import frida,psutil,sys

pid=None

for proc in psutil.process_iter(['name','pid','cmdline']):
    if 'python.exe' in proc.info['name'] and 'printf_loop.py' in ' '.join(proc.info['cmdline']):
        pid=proc.info['pid']
        break

if pid:
    session=frida.attach(pid)
    print(f"Process attached to PID: {pid}")

    js_code="""var mod = Process.findModuleByName("ucrtbase.dll");
                var target = null;
                
                if (mod)
                {
                    var addr=mod.findExportByName("__stdio_common_vfprintf");
                    if (addr)
                    {
                        target={module: "ucrtbase.dll", symbol: "__stdio_common_vfprintf", address:addr};
                    }
                }
                
                if (!target)
                {
                    console.log("__stdio_common_vfprintf not found in ucrtbase.dll");
                }
                else
                {
                    console.log("Hooking " + target.symbol + " on " + target.module + " @ " +target.address);
                    Interceptor.attach(target.address,
                    {
                        onEnter: function (args)
                        {
                            console.log(" H I T");
                            console.log("formats: ", args[2].readUtf8String());

                            var va_list=args[4];
                            var counterVar=va_list.readS32();
                            var replacement=Math.floor(Math.random()*100)+1;
                            console.log("Original: ",counterVar," ->Replaced: ",replacement);
                            va_list.writeS32(replacement);
                        }
                    })
                }"""

    def on_message(message,data):
        print(message)

    script=session.create_script(js_code)
    script.on("message",on_message)
    script.load()
    print("Hook installed, press Ctrl + c to quit")
    sys.stdin.read()