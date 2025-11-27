from quart import Quart, request, jsonify

def createAPI(queue):
    PiTunes = Quart(__name__)

    @PiTunes.get("/state")
    async def getState():
        return jsonify(await queue.snapshot())

    @PiTunes.post("/skip")
    async def skip():
        voter = request.remote_addr
        ok, skipNow = await queue.voteSkip(voter)
        return {"voted": ok, "skipped": skipNow}

    @PiTunes.post("/endTurn")
    async def endTurn():
        new_current = await queue.endTurn()
        return {"new_current": new_current}

    return PiTunes
