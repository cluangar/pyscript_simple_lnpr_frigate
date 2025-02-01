@service
def lnpr_s(event_id=None, FRIGATE_HOST = "http://172.16.200.184:5000", LNPR_API = "http://172.16.200.107:8502/alpr"):

  import datetime
  import io
  import sys
  import json
  import shutil
  import requests
  from PIL import Image as im

  if "/config/pyscript_modules" not in sys.path:
    sys.path.append("/config/pyscript_modules")

  logfile = "/config/www/detected_plates.log"

  # host for frigate instance
  #FRIGATE_HOST = "http://ccab4aaf-frigate:5000"

  # host for CodeProject.AI instance
  #LNPR_HOST = "http://172.16.200.107:8502"

#  json = requests.get(f"{FRIGATE_HOST}/api/events/{event_id}").json()
#  camera = json["camera"]

  url = FRIGATE_HOST + "/api/events/" + str(event_id)
  r = task.executor(requests.get, url)
  json_r = r.json()
  camera = json_r["camera"]

  if json_r.get("data").get("attributes"):
    attributes = json_r["data"]["attributes"]
  else:
    attributes = None

  # Checks to ensure that license plate is detected
  # this will need to be removed if not using a model that detects license plates (like frigate+)
  if not attributes:

      data = "[" + str(datetime.datetime.now()) + "]: " + camera + " - could not find license plate in " + str(json_r) + "\n"
      task.executor(read_write_file, logfile, data)

#          sys.exit()


  #**No frigate+ Model to detect license_plate
  #box = json["data"]["box"]
  if attributes:
    box = attributes[0]["box"]
  else:
    box = None

#  detect = requests.get(f"{FRIGATE_HOST}/api/config").json()["cameras"][camera]["detect"]
  url = FRIGATE_HOST + "/api/config"
  r = task.executor(requests.get, url)
  json_r = r.json()
  detect = json_r["cameras"][camera]["detect"]

  known_res = (detect["width"], detect["height"])

  # find coordinates of image to send to detector
  if box:
    x_mid = (box[0] + (box[2] / 2)) * known_res[0]
    y_max = (box[1] + box[3]) * known_res[1]

#  cropped_image = img.crop((max(0, x_mid - 150), 0, min(known_res[0], x_mid + 150), known_res[1]))
#  cropped_image.save("/config/bashscript/crop.jpg")

  # you will likely need to create multiple iterations for each vehicle
  # 0/8/B for example are often mixed up
  known_plates = {
      # Bob's Car
      "ABC128": "Bob's Car",
      "ABC12B": "Bob's Car",
    
      # Steve's Truck
      "123TR0": "Steve's Truck",
      "123TRO": "Steve's Truck",
  }

###########
  #calc url download picture from frigate server
  #http://172.16.200.184:5000/api/events/<event_id>/snapshot.jpg?bbox=0
  #http://172.16.200.184:5000/api/<cam>/recordings/<time>/snapshot.png
  url = FRIGATE_HOST + "/api/events/" + event_id + "/snapshot.jpg?bbox=0"
  start_time = event_id.split("-")
  start_time = start_time[0]
  url2 = FRIGATE_HOST + "/api/" + camera + "/recordings/" + start_time + "/snapshot.png"
  filename = event_id + ".jpg"
###########
#  with open('/config/bashscript/crop.jpg', 'rb') as fp:
#      response = requests.post(
#          f'{LNPR_HOST}/alpr/',
#          files=dict(upload=fp),
#      )
#      print(response.json())
#      plates = response.json()
#      plate = None
  JSON_HEADERS = {
       "accept": "application/json",
       "Content-Type": "application/json; charset=utf-8"
  }
  payload = { "url": url,
              "h_url": url2,
              "filename": filename,
              "cam_user": "",
              "cam_pass": "",
  }

#LNPR API Server
  r = task.executor(requests.post, LNPR_API, headers = JSON_HEADERS, json = payload)
#  log.info(r.json())

  plate = None
  score = None
  if r:
      plates = r.json()
#      plate = None
#      score = None

#      if (not plates["license_number"] == ""):
      plate = str(plates["license_number"])
      score = plates["license_number_score"]


#      log.info(f"Checking plate: {plate} in {known_plates.keys()}")

#      with open("/config/bashscript/detected_plates.log", "a") as log:
#          log.write(f"[{datetime.datetime.now()}]: {camera} - detected {plate} as {known_plates.get(plate)} with a score of {score}\n")

      if known_plates.get(plate):
          report_plate = known_plates.get(plate)
      else:
          report_plate = plate

      data = "[" + str(datetime.datetime.now()) + "]: " + camera + " - detected " + str(plate) + " as " + str(report_plate) + " with a score of " + str(score) + "\n"
      task.executor(read_write_file, logfile, data)

#      if plate in known_plates.keys():
#          log.info(f"{camera} - Found a known plate: {known_plates[plate]}")
#      else:
#          plate = None

  else:
#      with open("/config/bashscript/detected_plates.log", "a") as log:
#          log.write(f"[{datetime.datetime.now()}]: {camera} - No plates detected in run: {plates}\n")
      data = "[" + str(datetime.datetime.now()) + "]: " + camera + " - No plates detected in run: " + str(plate) + "\n"
      task.executor(read_write_file, logfile, data)


  if plate is None:
      log.info(f"No valid results found")
      return
#      sys.exit()


#  vehicle_name = known_plates[plate]
  #***Need add known and unknown to frigate
  if known_plates.get(plate):
      vehicle_name = known_plates[plate]
  else:
      vehicle_name = plate


  # Add Sub Label To Car Event
#  requests.post(f"{FRIGATE_HOST}/api/events/{event_id}/sub_label", json={"subLabel": vehicle_name, "subLabelScore": round(score, 2)})
  url = FRIGATE_HOST + "/api/events/" + event_id + "/sub_label"
  
  if score is not None or score != "":
#      score_f = round( float(score.strip('[]')), 2)
#      score_f = round( (float(score) * 100), 0)
#      score_f = round( float(score) * 100, 2)
#      score_f = round( float(score) * 1, 2)
      score_f = round(score, 2)
#**bug in frigate miss float or string
#  score_f = None

  payload = {
      "subLabel": vehicle_name ,
      "subLabelScore": score_f ,
  }
  r = task.executor(requests.post, url, headers = JSON_HEADERS, json = payload )


  #Debug Log
  log.info(f"Run lnpr Finish")
#  notify.persistent_notification(message=f"url={url}, url2={url2}, filename={filename}", title="lnpr pyscript")
#  notify.persistent_notification(message=f"Results={plates}", title="lnpr pyscript")
#  notify.persistent_notification(message=f"Test Return event_id={event_id}, Cam={camera}", title="lnpr pyscript")
#  notify.persistent_notification(message=f"Raw Plate ={plate}, Name Plate={vehicle_name}, Score={str(score_f)}", title="lnpr pyscript")
  notify.persistent_notification(message=f"Frigate Update Payload ={payload}", title="lnpr pyscript")



@pyscript_compile
def read_write_file(filename, data):

  with open(filename, "a") as log:
      log.write(f"{data}")

  return
