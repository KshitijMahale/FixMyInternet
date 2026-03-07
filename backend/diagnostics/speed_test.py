import speedtest

def run_speed_test():
    try:
        st = speedtest.Speedtest()

        # find best test server
        st.get_best_server()
        download_speed = st.download()
        upload_speed = st.upload()

        results = {
            "download_mbps": round(download_speed / 1_000_000, 2),
            "upload_mbps": round(upload_speed / 1_000_000, 2)
        }

        return results

    except Exception:
        return {
            "download_mbps": None,
            "upload_mbps": None
        }