package org.altbeacon.beaconreference;

import android.app.Application;
import android.app.Notification;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.app.TaskStackBuilder;
import android.content.Context;
import android.content.Intent;

import android.os.Build;
import android.util.Log;
import android.widget.Toast;

import com.android.volley.Request;
import com.android.volley.RequestQueue;
import com.android.volley.Response;
import com.android.volley.toolbox.JsonObjectRequest;
import com.android.volley.toolbox.Volley;

import org.altbeacon.beacon.BeaconManager;
import org.altbeacon.beacon.BeaconParser;
import org.altbeacon.beacon.Identifier;
import org.altbeacon.beacon.MonitorNotifier;
import org.altbeacon.beacon.Region;
import org.altbeacon.beacon.logging.LogManager;
import org.altbeacon.beacon.service.MonitoringStatus;
import org.json.JSONException;
import org.json.JSONObject;

/**
 * Created by dyoung on 12/13/13.
 */
public class BeaconReferenceApplication extends Application implements MonitorNotifier {
    private static final String TAG = "BeaconReferenceApp";
    //public static final Region wildcardRegion = new Region("wildcardRegion", null,null,null);
    public static final Region region1 = new Region("HF", Identifier.parse("0xedd1ebeac04e5defa017")
            ,Identifier.parse("0xf8804a959b10"),null);
    public static final Region region2 = new Region("Bar", Identifier.parse("0xedd1ebeac04e5defa017")
            , Identifier.parse("0xcfbf822eadf9"),null);
    public static final Region region3 = new Region("Comedor", Identifier.parse("0xedd1ebeac04e5defa017")
            , Identifier.parse("0xeed84d40a395"),null);
    public static boolean insideRegion = false;

    private static String uuid = null;

    public static void setUuid(String uuidAux){
        uuid = uuidAux;
    }
    public static String getUuid(){
        return uuid;
    }
    public void onCreate() {
        super.onCreate();
        BeaconManager beaconManager = org.altbeacon.beacon.BeaconManager.getInstanceForApplication(this);
        beaconManager.getBeaconParsers().add(new BeaconParser().
                setBeaconLayout(BeaconParser.EDDYSTONE_UID_LAYOUT));
        SplashActivity.id(this.getApplicationContext());
        uuid = SplashActivity.getDevId();
        // By default the AndroidBeaconLibrary will only find AltBeacons.  If you wish to make it
        // find a different type of beacon, you must specify the byte layout for that beacon's
        // advertisement with a line like below.  The example shows how to find a beacon with the
        // same byte layout as AltBeacon but with a beaconTypeCode of 0xaabb.  To find the proper
        // layout expression for other beacon types, do a web search for "setBeaconLayout"
        // including the quotes.
        //
        //beaconManager.getBeaconParsers().clear();
        //beaconManager.getBeaconParsers().add(new BeaconParser().
        //        setBeaconLayout("m:2-3=beac,i:4-19,i:20-21,i:22-23,p:24-24,d:25-25"));

        beaconManager.setDebug(true);


        // Uncomment the code below to use a foreground service to scan for beacons. This unlocks
        // the ability to continually scan for long periods of time in the background on Andorid 8+
        // in exchange for showing an icon at the top of the screen and a always-on notification to
        // communicate to users that your app is using resources in the background.
        //


        Notification.Builder builder = new Notification.Builder(this);
        builder.setSmallIcon(R.drawable.ic_launcher);
        builder.setContentTitle("Scanning for Beacons");
        Intent intent = new Intent(this, SplashActivity.class);
        PendingIntent pendingIntent = PendingIntent.getActivity(
                this, 0, intent, PendingIntent.FLAG_UPDATE_CURRENT
        );

        builder.setContentIntent(pendingIntent);
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            NotificationChannel channel = new NotificationChannel("My Notification Channel ID",
                    "My Notification Name", NotificationManager.IMPORTANCE_DEFAULT);
            channel.setDescription("My Notification Channel Description");
            NotificationManager notificationManager = (NotificationManager) getSystemService(
                    Context.NOTIFICATION_SERVICE);
            notificationManager.createNotificationChannel(channel);
            builder.setChannelId(channel.getId());
        }
        beaconManager.enableForegroundServiceScanning(builder.build(), 456);

        // For the above foreground scanning service to be useful, you need to disable
        // JobScheduler-based scans (used on Android 8+) and set a fast background scan
        // cycle that would otherwise be disallowed by the operating system.
        //
        beaconManager.setEnableScheduledScanJobs(false);
        beaconManager.setBackgroundBetweenScanPeriod(0);
        beaconManager.setBackgroundScanPeriod(1100);




        Log.d(TAG, "setting up background monitoring in app onCreate");
        beaconManager.addMonitorNotifier(this);

        // If we were monitoring *different* regions on the last run of this app, they will be
        // remembered.  In this case we need to disable them here
        for (Region region: beaconManager.getMonitoredRegions()) {
            beaconManager.stopMonitoring(region);
        }

        beaconManager.startMonitoring(region1);
        beaconManager.startMonitoring(region2);
        beaconManager.startMonitoring(region3);

        // If you wish to test beacon detection in the Android Emulator, you can use code like this:
        // BeaconManager.setBeaconSimulator(new TimedBeaconSimulator() );
        // ((TimedBeaconSimulator) BeaconManager.getBeaconSimulator()).createTimedSimulatedBeacons();
    }

    @Override
    public void didEnterRegion(Region arg0) {
        Log.d(TAG, "did enter region.");
        insideRegion = true;
        // Send a notification to the user whenever a Beacon
        // matching a Region (defined above) are first seen.
        Log.d(TAG, "Sending notification.");
        if(uuid == null){

        }
        else{
            String id = SplashActivity.getDevId();
            enter(id, arg0);
            sendNotification("Entrando en la región" + arg0.getUniqueId());
        }

    }

    @Override
    public void didExitRegion(Region region) {
        insideRegion = false;
        // do nothing here. logging happens in MonitoringActivity
        if(uuid == null){

        }
        else{
            sendNotification("Saliendo de la región" + region.getUniqueId());
            String id = SplashActivity.getDevId();
            exit(id, region);
        }
    }


    private void enter(String id,Region region){
        RequestQueue volleyQueue = Volley.newRequestQueue(BeaconReferenceApplication.this);
        String url = "https://tfg-u3xd.onrender.com/stays";
        JSONObject entrada = new JSONObject();
        try{
            entrada.put("room_name",region.getUniqueId());
            entrada.put("uuid", id);
        } catch(JSONException e){
            e.printStackTrace();
        }

        JsonObjectRequest jsonObjectRequest = new JsonObjectRequest(Request.Method.POST,url,entrada
            ,(Response.Listener<JSONObject>) response-> {
                String rsp;
                try{
                    Log.d("respuesta", response.getString("message"));
                }
                catch (JSONException e){
                    e.printStackTrace();
            }
        },
        (Response.ErrorListener) error -> {
            // make a Toast telling the user
            // that something went wrong
            Toast.makeText(BeaconReferenceApplication.this, "Ha ocurrido un error al guardar la estancia",
                    Toast.LENGTH_LONG).show();
            // log the error message in the error stream
            Log.e("MainActivity", "loadDogImage error: ${error.localizedMessage}");
        });
        volleyQueue.add(jsonObjectRequest);
    }

    private void exit(String id, Region region){
        RequestQueue volleyQueue = Volley.newRequestQueue(BeaconReferenceApplication.this);
        String url = "https://tfg-u3xd.onrender.com/stays";
        JSONObject entrada = new JSONObject();
        try{
            entrada.put("room_name",region.getUniqueId());
            entrada.put("uuid", id);
        } catch(JSONException e){
            e.printStackTrace();
        }

        JsonObjectRequest jsonObjectRequest = new JsonObjectRequest(Request.Method.PUT,url,entrada
                ,(Response.Listener<JSONObject>) response-> {
            String rsp;
            try{
                Log.d("respuesta", response.getString("message"));
            }
            catch (JSONException e){
                e.printStackTrace();
            }
        },
                (Response.ErrorListener) error -> {
                    // make a Toast telling the user
                    // that something went wrong
                    Toast.makeText(BeaconReferenceApplication.this, "Ha ocurrido un error al modificar la estancia" , Toast.LENGTH_LONG).show();
                    // log the error message in the error stream
                    Log.e("MainActivity", "loadDogImage error: ${error.localizedMessage}");
                });
        volleyQueue.add(jsonObjectRequest);
    }

    @Override
    public void didDetermineStateForRegion(int state, Region region) {
        // do nothing here. logging happens in MonitoringActivity
    }

    private void sendNotification(String text) {
        NotificationManager notificationManager =
                (NotificationManager) this.getSystemService(Context.NOTIFICATION_SERVICE);
        Notification.Builder builder;
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            NotificationChannel channel = new NotificationChannel("Beacon Reference Notifications",
                    "Beacon Reference Notifications", NotificationManager.IMPORTANCE_HIGH);
            channel.enableLights(true);
            channel.enableVibration(true);
            channel.setLockscreenVisibility(Notification.VISIBILITY_PUBLIC);
            notificationManager.createNotificationChannel(channel);
            builder = new Notification.Builder(this, channel.getId());
        }
        else {
            builder = new Notification.Builder(this);
            builder.setPriority(Notification.PRIORITY_HIGH);
        }

        TaskStackBuilder stackBuilder = TaskStackBuilder.create(this);
        stackBuilder.addNextIntent(new Intent(this, SplashActivity.class));
        PendingIntent resultPendingIntent =
                stackBuilder.getPendingIntent(
                        0,
                        PendingIntent.FLAG_UPDATE_CURRENT
                );
        builder.setSmallIcon(R.drawable.ic_launcher);
        builder.setContentTitle(text);
        builder.setContentText("Tap here to see details in the reference app");
        builder.setContentIntent(resultPendingIntent);
        notificationManager.notify(1, builder.build());
    }
}
