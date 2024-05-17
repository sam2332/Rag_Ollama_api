

from contextlib import closing
from fastapi import HTTPException
from Libs.DB import get_db_connection
from Libs.Utility import make_embeddings_safe_for_db
from Libs.RequestSchema import ChangeEmbeddingDBFilename, EmbeddingRequest, IngressEmbeddingsRequest


def register_routes(app):

    @app.post("/api/reset_embeddings_db")
    async def reset_embeddings_db():
        with get_db_connection() as conn:
            with closing(conn.cursor()) as cursor:
                cursor.execute("DELETE FROM embeddings")
                conn.commit()
        return {"status": "success"}




    @app.post("/api/change_embedding_db/")
    async def change_embedding_db(data: ChangeEmbeddingDBFilename):
        app.config.set("embeddings_db_model", data.name)
        if not os.path.exists(f"./embeddings/{data.name}.db"):
            setup_database()
        app.config.save()
        return {"status": "success"}
        


    # Endpoint to get all embeddings
    @app.get("/api/embeddings/")
    async def get_embeddings():
        with get_db_connection() as conn:
            with closing(conn.cursor()) as cursor:
                cursor.execute("SELECT * FROM embeddings")
                rows = cursor.fetchall()
                return [dict(row) for row in rows]





    def ingress_thread(file):
        if file.suffix == ".txt":
            with open(file, "r") as f:
                content = f.read()
                #chunk content 255 characters
                for i in range(0, len(content), data.chunk_size):
                    insert_embedding(content[i:i+255], file.name + " - chunk " + str(i))
        elif file.suffix == ".csv":
            file_data = file.read_text()
            lines = file_data.split("\n")
            avg_list = []
            for index in range(2, len(lines) - 1,5):

                start = time.time()
                content = ""
                for i in range(data.overlap):
                    if index-i >0:
                        content += lines[index-i] + "\n"
                content += lines[index] + "\n"

                for i in range(data.overlap):
                    if index+i < len(lines):
                        content += lines[index+i] + "\n"
                #add headers at top of content
                content = " ".join(lines[0:2]) + "\n" + content
                insert_embedding(content, file.name+" - line "+str(index))
                end = time.time()
                avg_list.append(end-start)
                avg = sum(avg_list)/len(avg_list)
                print(f"Average time: {avg} seconds, time remaining for {len(lines)-index} lines: {avg*(len(lines)-index)} seconds")
                avg_list = avg_list[-10:]

    @app.post("/api/ingress_file_embeddings/")
    async def ingress_file_embeddings(data: IngressEmbeddingsRequest):
        # Get all files in the ingress folder
        ingress_folder = Path("ingress")
        threads = []
        for file in ingress_folder.iterdir():
            if file.is_file():
                t = threadding.Thread(target=thread, args=(file,)).start()
                threads.append(t)
        for t in threads:
            t.join()
        return {"status": "success"}

    import threading as threadding
    from queue import Queue

    def ingress_thread(queue):
        failout = 5
        while failout >0:
            while not queue.empty():
                file, lines = queue.get()
                content = "\n".join(lines)
                try:
                    insert_embedding(content, file)
                except Exception as e:
                    print(e)
                    failout -= 1
            failout -1

    @app.post("/api/fast_csv_ingress/")
    async def fast_csv_ingress():
        queue = Queue()
        for file in Path('ingress').glob("*.csv"):
            lines = file.read_text().split("\n")
            threadding.Thread(target=ingress_thread, args=(queue,)).start()
            threadding.Thread(target=ingress_thread, args=(queue,)).start()
            threadding.Thread(target=ingress_thread, args=(queue,)).start()
            threadding.Thread(target=ingress_thread, args=(queue,)).start()
            threadding.Thread(target=ingress_thread, args=(queue,)).start()
            threadding.Thread(target=ingress_thread, args=(queue,)).start()
            threadding.Thread(target=ingress_thread, args=(queue,)).start()
            for index in range(2, len(lines) - 1, 5):
                queue.put((f"{file.name} - lines {index-2} - {index+2}", lines[index-2:index+3]))

        while queue.qsize() > 0:
            time.sleep(1)
        return {"status": "success"}
    def generate_embedding(prompt):
        response = requests.post(app.config.get('ollama_host')+"/api/embeddings", json={"model": app.config.get('embeddings_model'), "prompt": prompt})
        if response.status_code == 200:
            return response.json()['embedding']
        else:
            raise Exception("Error generating embeddings")



        

    def insert_embedding(content, source):
        print(f"Inserting embedding for {len(content)} bytes from {source}")
        response = requests.post(app.config.get('ollama_host')+"/api/embeddings", json={"model": app.config.get('embeddings_model'), "prompt": content})
        if response.status_code == 200:
            embedding = response.json()['embedding']
            with get_db_connection() as conn:
                with closing(conn.cursor()) as cursor:
                    embedding = make_embeddings_safe_for_db(embedding)
                    #check if exists
                
                    cursor.execute("INSERT INTO embeddings (source, content, embedding) VALUES (?, ?, ?)", (source, content, embedding))
                    conn.commit()
                    return {"status": "success", "content": content, "embedding": embedding}
        else:
            raise HTTPException(status_code=response.status_code, detail="Error processing embeddings")
    # Endpoint to insert text and embeddings
    @app.post("/api/insert_text_embeddings/")
    async def insert_text_embeddings(data: EmbeddingRequest):
        # Simulating external API call for embeddings
        return insert_embedding(data.content, data.source)