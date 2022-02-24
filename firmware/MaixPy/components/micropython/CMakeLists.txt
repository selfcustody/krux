if(CONFIG_COMPONENT_MICROPYTHON_ENABLE)
    set(mpy_component_name "micropython")
    get_filename_component(mpy_dir ${CMAKE_CURRENT_LIST_FILE} DIRECTORY)
    set(mpy_core_dir "${mpy_dir}/core")
    set(mpy_core_src_dir "${mpy_core_dir}/py")
    set(mpy_port_dir "${mpy_dir}/port")
    set(mpy_build_dir "${CMAKE_BINARY_DIR}/micropython")
    set(mpy_build_gen_header_dir "${mpy_build_dir}/genhdr")

    if(IS_DIRECTORY ${CONFIG_BUILTIN_PY_DIR})
        set(mpy_frozen_py_dir ${CONFIG_BUILTIN_PY_DIR})
    else()
        set(mpy_frozen_py_dir "${mpy_port_dir}/builtin_py")
    endif()
    message(STATUS "builtin py dir: ${mpy_frozen_py_dir}")
    set(mpy_build_mpy_dir "${mpy_build_dir}/mpy")
    set(lvgl_build_dir "${mpy_build_dir}/port/lvgl")
    set(lodepng_build_dir "${mpy_build_dir}/port/lodepng")
    set(components_requirements kendryte_sdk drivers boards utils spiffs)

    ################# Add include #################
    list(APPEND ADD_INCLUDE "${mpy_core_dir}"
                            "${mpy_core_src_dir}"
                            "${mpy_core_dir}/lib/oofatfs"
                            "${mpy_core_dir}/lib/mp-readline"
                            "${mpy_core_dir}/lib/utils"
                            "${mpy_core_dir}/lib/timeutils"
                            "${mpy_core_dir}/lib/memzip"
                            "${mpy_port_dir}/include"
                            "${mpy_port_dir}/src/Maix/include"
                            "${mpy_port_dir}/src/omv/include"
                            "${mpy_port_dir}/src/omv/boards/MAIX"
                            "${mpy_port_dir}/src/omv/img/include"
                            "${mpy_port_dir}/src/omv/py/include"
                            "${mpy_port_dir}/src/standard_lib/include"
                            "${mpy_build_dir}"
        )
    ###############################################

    

    ############## Add source files ###############
    append_srcs_dir(MPY_PORT_SRCS "port/src")
    append_srcs_dir(MPY_PORT_SRCS "port/src/Maix")
    append_srcs_dir(MPY_PORT_SRCS "port/src/omv")
    append_srcs_dir(MPY_PORT_SRCS "port/src/omv/img")
    append_srcs_dir(MPY_PORT_SRCS "port/src/omv/py")
    append_srcs_dir(MPY_PORT_SRCS "port/src/standard_lib/machine")
    append_srcs_dir(MPY_PORT_SRCS "port/src/standard_lib/uos")
    append_srcs_dir(MPY_PORT_SRCS "port/src/standard_lib/utime")
    list(APPEND MPY_PORT_SRCS "port/memzip-files.c")

    list(APPEND MPY_SRCS    
                    "core/py/mpstate.c"
                    "core/py/nlr.c"
                    "core/py/nlrx86.c"
                    "core/py/nlrx64.c"
                    "core/py/nlrthumb.c"
                    "core/py/nlrxtensa.c"
                    "core/py/nlrsetjmp.c"
                    "core/py/malloc.c"
                    "core/py/gc.c"
                    "core/py/pystack.c"
                    "core/py/qstr.c"
                    "core/py/vstr.c"
                    "core/py/mpprint.c"
                    "core/py/unicode.c"
                    "core/py/mpz.c"
                    "core/py/reader.c"
                    "core/py/lexer.c"
                    "core/py/parse.c"
                    "core/py/scope.c"
                    "core/py/compile.c"
                    "core/py/emitcommon.c"
                    "core/py/emitbc.c"
                    "core/py/asmbase.c"
                    "core/py/asmx64.c"
                    "core/py/emitnx64.c"
                    "core/py/asmx86.c"
                    "core/py/emitnx86.c"
                    "core/py/asmthumb.c"
                    "core/py/emitnthumb.c"
                    "core/py/emitinlinethumb.c"
                    "core/py/asmarm.c"
                    "core/py/emitnarm.c"
                    "core/py/asmxtensa.c"
                    "core/py/emitnxtensa.c"
                    "core/py/emitinlinextensa.c"
                    "core/py/formatfloat.c"
                    "core/py/parsenumbase.c"
                    "core/py/parsenum.c"
                    "core/py/emitglue.c"
                    "core/py/persistentcode.c"
                    "core/py/runtime.c"
                    "core/py/runtime_utils.c"
                    "core/py/scheduler.c"
                    "core/py/nativeglue.c"
                    "core/py/stackctrl.c"
                    "core/py/argcheck.c"
                    "core/py/warning.c"
                    "core/py/map.c"
                    "core/py/obj.c"
                    "core/py/objarray.c"
                    "core/py/objattrtuple.c"
                    "core/py/objbool.c"
                    "core/py/objboundmeth.c"
                    "core/py/objcell.c"
                    "core/py/objclosure.c"
                    "core/py/objcomplex.c"
                    "core/py/objdeque.c"
                    "core/py/objdict.c"
                    "core/py/objenumerate.c"
                    "core/py/objexcept.c"
                    "core/py/objfilter.c"
                    "core/py/objfloat.c"
                    "core/py/objfun.c"
                    "core/py/objgenerator.c"
                    "core/py/objgetitemiter.c"
                    "core/py/objint.c"
                    "core/py/objint_longlong.c"
                    "core/py/objint_mpz.c"
                    "core/py/objlist.c"
                    "core/py/objmap.c"
                    "core/py/objmodule.c"
                    "core/py/objobject.c"
                    "core/py/objpolyiter.c"
                    "core/py/objproperty.c"
                    "core/py/objnone.c"
                    "core/py/objnamedtuple.c"
                    "core/py/objrange.c"
                    "core/py/objreversed.c"
                    "core/py/objset.c"
                    "core/py/objsingleton.c"
                    "core/py/objslice.c"
                    "core/py/objstr.c"
                    "core/py/objstrunicode.c"
                    "core/py/objstringio.c"
                    "core/py/objtuple.c"
                    "core/py/objtype.c"
                    "core/py/objzip.c"
                    "core/py/opmethods.c"
                    "core/py/sequence.c"
                    "core/py/stream.c"
                    "core/py/binary.c"
                    "core/py/builtinimport.c"
                    "core/py/builtinevex.c"
                    "core/py/builtinhelp.c"
                    "core/py/modarray.c"
                    "core/py/modbuiltins.c"
                    "core/py/modcollections.c"
                    "core/py/modgc.c"
                    "core/py/modio.c"
                    "core/py/modmath.c"
                    "core/py/modcmath.c"
                    "core/py/modmicropython.c"
                    "core/py/modstruct.c"
                    "core/py/modsys.c"
                    "core/py/moduerrno.c"
                    "core/py/modthread.c"
                    "core/py/vm.c"
                    "core/py/bc.c"
                    "core/py/showbc.c"
                    "core/py/repl.c"
                    "core/py/smallint.c"
                    "core/py/frozenmod.c"
            )

    list(APPEND MPY_EXTMOD_SRCS 
                        "core/extmod/moductypes.c"
                        "core/extmod/modujson.c"
                        "core/extmod/moduzlib.c"
                        "core/extmod/moduheapq.c"
                        "core/extmod/modutimeq.c"
                        "core/extmod/moducryptolib.c"
                        "core/extmod/modubinascii.c"
                        "core/extmod/virtpin.c"
                        "core/extmod/machine_mem.c"
                        "core/extmod/machine_pinbase.c"
                        "core/extmod/machine_signal.c"
                        "core/extmod/machine_pulse.c"
                        "core/extmod/machine_i2c.c"
                        "core/extmod/machine_spi.c"
                        "core/extmod/modurandom.c"
                        "core/extmod/moduselect.c"
                        "core/extmod/modframebuf.c"
                        "core/extmod/vfs.c"
                        "core/extmod/vfs_reader.c"
                        "core/extmod/vfs_posix.c"
                        "core/extmod/vfs_posix_file.c"
                        "core/extmod/vfs_fat.c"
                        "core/extmod/vfs_fat_diskio.c"
                        "core/extmod/vfs_fat_file.c"
                        "core/extmod/utime_mphal.c"
                        "core/extmod/uos_dupterm.c"
                        "core/lib/embed/abort_.c"
                        "core/lib/utils/printf.c"
                        "core/lib/utils/stdout_helpers.c"
                        "core/lib/utils/interrupt_char.c"
                        "core/lib/utils/pyexec.c"
                        "core/lib/libc/string0.c"
                        "core/lib/mp-readline/readline.c"
                        "core/lib/timeutils/timeutils.c"
                        "core/lib/utils/sys_stdio_mphal.c"
                        "core/lib/oofatfs/ff.c"
                        "core/lib/oofatfs/ffunicode.c"
                        "core/lib/memzip/import.c"
                        "core/lib/memzip/lexermemzip.c"
                        "core/lib/memzip/memzip.c"
                    )
    set(MPY_FROZEN_SRC "${mpy_build_dir}/frozen_mpy.c")

    list(APPEND ADD_SRCS    ${MPY_SRCS}
                            ${MPY_PORT_SRCS}
                            ${MPY_EXTMOD_SRCS}
                            ${MPY_FROZEN_SRC}
                            )
    # list(APPEND ADD_SRCS_GENERATED ${MPY_FROZEN_SRC})
    set_property(SOURCE ${MPY_FROZEN_SRC} PROPERTY GENERATED 1)
    ###############################################


    ############# OPTIONAL MODULES PART 1 ##############
    # touch screen
    if(CONFIG_MAIXPY_TOUCH_SCREEN_ENABLE)
        list(APPEND ADD_INCLUDE "${mpy_port_dir}/src/touchscreen/include"
                                )
        append_srcs_dir(ADD_SRCS "port/src/touchscreen")
        if(CONFIG_MAIXPY_TOUCH_SCREEN_DRIVER_NS2009)
            list(APPEND ADD_INCLUDE "${mpy_port_dir}/src/touchscreen/ns2009/include")
            append_srcs_dir(ADD_SRCS "port/src/touchscreen/ns2009")
        endif()
        if(CONFIG_MAIXPY_TOUCH_SCREEN_DRIVER_FT52XX)
            list(APPEND ADD_INCLUDE "${mpy_port_dir}/src/touchscreen/ft52xx"
                                    "${mpy_port_dir}/src/touchscreen/ns2009/include")
            append_srcs_dir(ADD_SRCS "port/src/touchscreen/ft52xx")
            append_srcs_dir(ADD_SRCS "port/src/touchscreen/ns2009")
        endif()
    endif()
    # omv minimum
    if(CONFIG_MAIXPY_OMV_MINIMUM)
        # TODO:
        message(STATUS "OMV minimum enabled")
    endif()
    # LVGL
    set(LVGL_MPY_GEN_SRC "")
    # lodepng
    set(LODEPNG_MPY_GEN_SRC "")
    list(APPEND ADD_INCLUDE "${mpy_port_dir}/src/secp256k1-embedded/secp256k1"
                            "${mpy_port_dir}/src/secp256k1-embedded/secp256k1/src"
                            "${mpy_port_dir}/src/secp256k1-embedded/mpy/config"
                            )
    list(APPEND ADD_SRCS "port/src/secp256k1-embedded/secp256k1/src/secp256k1.c")
    list(APPEND ADD_SRCS "port/src/secp256k1-embedded/mpy/config/ext_callbacks.c")
    list(APPEND ADD_SRCS "port/src/secp256k1-embedded/mpy/libsecp256k1.c")
    set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -DHAVE_CONFIG_H")
    list(APPEND ADD_INCLUDE "${mpy_port_dir}/src/uhashlib/crypto"
                            "${mpy_port_dir}/src/uhashlib"
                            )
    append_srcs_dir(ADD_SRCS "port/src/uhashlib/crypto")
    append_srcs_dir(ADD_SRCS "port/src/uhashlib")
    list(APPEND ADD_INCLUDE "${mpy_port_dir}/src/qrcode/qrcodegen"
                            "${mpy_port_dir}/src/qrcode"
                            )
    append_srcs_dir(ADD_SRCS "port/src/qrcode/qrcodegen")
    append_srcs_dir(ADD_SRCS "port/src/qrcode")
    list(APPEND ADD_INCLUDE "${mpy_port_dir}/src/flash")
    append_srcs_dir(ADD_SRCS "port/src/flash")

    #############################################

    ################## FLAGS ####################
    # find requirements include  //TODO: maybe cmake have functio or variable can do this
    set(include_dir_flags ${ADD_INCLUDE})
    prepend(include_dir_flags "-I" ${include_dir_flags})
    foreach(component ${components_requirements})
        get_target_property(include_dir ${component} INTERFACE_INCLUDE_DIRECTORIES)    
        prepend(include_dir "-I" ${include_dir})
        list(APPEND include_dir_flags ${include_dir})
    endforeach()
    string(REPLACE ";" " " include_dir_flags "${include_dir_flags}")
    separate_arguments(cmd_param_cflag NATIVE_COMMAND ${CMAKE_C_FLAGS})
    separate_arguments(cmd_param_cinclude NATIVE_COMMAND ${include_dir_flags})
    #############################################

    ############ QSTR(SRC_QSTR) ##############
    set(QSTR_SRCS ${ADD_SRCS})
    list(REMOVE_ITEM QSTR_SRCS  "core/py/nlr.c"
                                "core/py/nlrsetjmp.c"
                                "core/py/nlrthumb.c"
                                "core/py/nlrx64.c"
                                "core/py/nlrx86.c"
                                "core/py/nlrxtensa.c"
                                ${MPY_FROZEN_SRC}
                        )

    # add version header
    set(version_header ${mpy_build_gen_header_dir}/mpversion.h)
    add_custom_target(gen_version_header
                            COMMAND mkdir -p ${mpy_build_gen_header_dir}
                            COMMAND ${python} ${mpy_core_src_dir}/makeversionhdr.py ${version_header}
                            DEPENDS ${LVGL_MPY_GEN_SRC} ${LODEPNG_SRC_C} ${LODEPNG_MPY_GEN_SRC}
                            VERBATIM
                        )


    # add qstr header
    set(qstr_header ${mpy_build_gen_header_dir}/qstrdefs.generated.h)
    # set_property(SOURCE ${qstr_header} PROPERTY GENERATED 1)
    set(PY_QSTR_DEFS ${mpy_core_src_dir}/qstrdefs.h)
    set(QSTR_DEFS    ${mpy_port_dir}/include/qstrdefsport.h)
    set(MODULE_DEFS ${mpy_build_gen_header_dir}/moduledefs.h)
    set(QSTR_DEFS_COLLECTED ${mpy_build_gen_header_dir}/qstrdefs.collected.h)
    set(QSTR_GEN_EXTRA_CFLAGS -DNO_QSTR -I${mpy_build_dir}/tmp)
    set(QSTR_GLOBAL_DEPENDENCIES ${mpy_core_src_dir}/mpconfig.h ${mpy_port_dir}/include/mpconfigport.h ${global_config_dir}/global_config.h)

    add_custom_target(gen_module_defs
            COMMAND ${python} ${mpy_core_src_dir}/makemoduledefs.py --vpath=${mpy_dir}, ${mpy_dir},  ${QSTR_SRCS} > ${MODULE_DEFS}
            DEPENDS gen_version_header
            VERBATIM
        )

    abspath(QSTR_SRCS_FULL_PATH ${QSTR_SRCS})
    add_custom_target(gen_qstr_i_last 
            COMMAND ${CMAKE_C_COMPILER} -E ${QSTR_GEN_EXTRA_CFLAGS} ${cmd_param_cflag} ${cmd_param_cinclude} -DFFCONF_H="${mpy_core_dir}/lib/oofatfs/ffconf.h" ${QSTR_SRCS_FULL_PATH} ${QSTR_GLOBAL_DEPENDENCIES} > ${mpy_build_gen_header_dir}/qstr.i.last
            DEPENDS gen_module_defs ${QSTR_GLOBAL_DEPENDENCIES} ${QSTR_SRCS}
            VERBATIM
        )
    add_custom_target(gen_collected_h
            COMMAND ${python} ${mpy_core_src_dir}/makeqstrdefs.py split ${mpy_build_gen_header_dir}/qstr.i.last ${mpy_build_gen_header_dir}/qstr ${QSTR_DEFS_COLLECTED}
            COMMAND touch ${mpy_build_gen_header_dir}/qstr.split
            COMMAND ${python} ${mpy_core_src_dir}/makeqstrdefs.py cat ${mpy_build_gen_header_dir}/qstr.i.last ${mpy_build_gen_header_dir}/qstr ${QSTR_DEFS_COLLECTED}
            DEPENDS gen_qstr_i_last
            VERBATIM
        )
    add_custom_target(gen_mpy_cross  
            COMMAND ${CMAKE_MAKE_PROGRAM} -C ${mpy_core_dir}/mpy-cross
            COMMENT "Generate mpy-cross ..."
        )
    separate_arguments(cmd_sed0 NATIVE_COMMAND "s/^Q(.*)/\"&\"/")
    separate_arguments(cmd_sed1 NATIVE_COMMAND "s/^\"\\(Q(.*)\\)\"/\\1/")
    
    add_custom_command(OUTPUT ${mpy_build_gen_header_dir}/qstrdefs.preprocessed.h
                    COMMAND cat ${PY_QSTR_DEFS} ${QSTR_DEFS} ${QSTR_DEFS_COLLECTED} | sed '${cmd_sed0}' | ${CMAKE_C_COMPILER} -E ${cmd_param_cflag} ${cmd_param_cinclude} - | sed '${cmd_sed1}' > ${mpy_build_gen_header_dir}/qstrdefs.preprocessed.h
                    DEPENDS gen_mpy_cross gen_version_header gen_module_defs gen_collected_h gen_qstr_i_last ${QSTR_DEFS_COLLECTED}
                )
    add_custom_command(OUTPUT ${qstr_header}
                    COMMAND ${python} ${mpy_core_src_dir}/makeqstrdata.py ${mpy_build_gen_header_dir}/qstrdefs.preprocessed.h > ${qstr_header}
                    DEPENDS ${mpy_build_gen_header_dir}/qstrdefs.preprocessed.h gen_qstr_i_last
                )

    set(frozen_py "${mpy_frozen_py_dir}/board.py")
    list(APPEND frozen_py "${mpy_frozen_py_dir}/fpioa_manager.py")
    foreach(py ${frozen_py})
        get_filename_component(py_name ${py} NAME)
        string(REPLACE ".py" "" py_name ${py_name})
        string(REPLACE ".py" ".mpy" mpy ${py})
        set(mpy_path ${mpy_build_mpy_dir}/${py_name}.mpy)
        list(APPEND frozen_mpy ${mpy_path})
        add_custom_command(OUTPUT ${mpy_path} 
                            COMMAND mkdir -p ${mpy_build_mpy_dir}
                            DEPENDS ${py}
                            COMMAND ${mpy_core_dir}/mpy-cross/mpy-cross -o ${mpy_path} -s ${py_name}.py ${py}
                    )
        # add_custom_target("mpy_${py_name}_target" DEPENDS ${mpy})
    endforeach()
    add_custom_command(OUTPUT ${MPY_FROZEN_SRC}
                COMMAND ${python} ${mpy_core_dir}/tools/mpy-tool.py -f -q ${mpy_build_gen_header_dir}/qstrdefs.preprocessed.h ${frozen_mpy} > ${MPY_FROZEN_SRC}
                DEPENDS ${qstr_header} ${frozen_mpy} 
            )

    ################################

    ###### Add required/dependent components ######
    list(APPEND ADD_REQUIREMENTS ${components_requirements})
    ###############################################

    ############ Add static libs ##################
    # list(APPEND ADD_STATIC_LIB "lib/libtest.a")
    ###############################################
    add_definitions(-DFFCONF_H=\"${mpy_core_dir}/lib/oofatfs/ffconf.h\"
                    -DNOT_GEN_MPY_CROSS=1
                    )

    register_component()

endif()

