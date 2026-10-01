# The port's targets, included by the generated build with
# -DWIIKIT_EXTRA=<this file>: the game's own layer linked into wiiboot.
target_sources(wiiboot PRIVATE ${CMAKE_CURRENT_LIST_DIR}/tls.cpp)
