package org.altbeacon.beaconreference;

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
import com.fasterxml.jackson.core.JsonParseException;
import com.fasterxml.jackson.databind.JsonMappingException;
import com.fasterxml.jackson.databind.ObjectMapper;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.io.IOException;
import java.text.SimpleDateFormat;
import java.time.LocalDate;
import java.time.format.DateTimeFormatter;
import java.util.Calendar;
import java.util.HashMap;
import java.util.Locale;
import java.util.Map;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.ScheduledFuture;
import java.util.concurrent.TimeUnit;

public class Notification_aux implements Runnable {
    Context mContext;
    public Double media;
    public Integer ocupacion_actual;

    public Double factor;
    public String room_name;
    public Integer i;
    public Boolean terminado = false;
    public Double cantidad_personas;
    private ScheduledExecutorService executor;
    private ScheduledFuture<?> scheduledFuture;

    public Notification_aux(Context mContext, String room_name, Double cantidad_personas){
        this.mContext = mContext;
        this.i = 0;
        this.room_name = room_name;
        this.cantidad_personas = cantidad_personas;
        run();
    }

    private void ejecutarCodigo(String cadena) {
        sendNotification(cadena);
    }
    private void haOcurridoAlgo() {

        Double factor = cantidad_personas * media;
        this.factor = factor;
        if(ocupacion_actual <= cantidad_personas * media){
            terminado = true;
        }
        else{
            terminado = false;
        }
        ejec();
    }
    private void getMedia(String input) {
        RequestQueue volleyQueue = Volley.newRequestQueue(this.mContext);
        String url = "https://tfg-u3xd.onrender.com/stays/mean";
        JSONObject entrada = new JSONObject();
        try{
            Locale spanishLocale=new Locale("es", "ES");
            Calendar cal = Calendar.getInstance();
            cal.add(Calendar.DATE, -7);
            SimpleDateFormat formmat1 = new SimpleDateFormat("yyyy-MM-dd");
            String formated = formmat1.format(cal.getTime());
            entrada.put("room_name",input);
            entrada.put("day", formated);
            //Toast.makeText(this.mContext, formated, Toast.LENGTH_LONG).show();
        } catch(JSONException e){
            e.printStackTrace();
        }
        JsonObjectRequest jsonObjectRequest = new JsonObjectRequest(Request.Method.POST,url,entrada
                ,(Response.Listener<JSONObject>) response-> {

            try {
                media = Double.valueOf(response.get("message").toString());
                getOcupacion(input);
            } catch (JSONException e) {
                throw new RuntimeException(e);
            }

        },
                (Response.ErrorListener) error -> {
                    // make a Toast telling the user
                    // that something went wrong

                    // log the error message in the error stream
                    error.printStackTrace();
                    Log.e("MainActivity", error.toString());
                    Log.e("MainActivity", url);
                    Log.e("MainActivity", entrada.toString());

                });
        volleyQueue.add(jsonObjectRequest);

    }
    private String getOcupacion(String input) {
        RequestQueue volleyQueue = Volley.newRequestQueue(this.mContext);
        String url = "https://tfg-u3xd.onrender.com/stays/room/occupation";
        JSONObject entrada = new JSONObject();
        JsonObjectRequest jsonObjectRequest = new JsonObjectRequest(Request.Method.POST,url,entrada
                ,(Response.Listener<JSONObject>) response-> {
            try {
                String cadenab  = response.getJSONObject("message").toString();
                Map<String, String> mapping = new ObjectMapper().readValue(cadenab, HashMap.class);

                for(String key : mapping.keySet()){

                    if(key.equals(room_name)){
                        ocupacion_actual = Integer.valueOf(mapping.get(key));
                        haOcurridoAlgo();

                    }
                }

            } catch (JSONException e) {
                throw new RuntimeException(e);
            } catch (JsonMappingException e) {
                throw new RuntimeException(e);
            } catch (JsonParseException e) {
                throw new RuntimeException(e);
            } catch (IOException e) {
                throw new RuntimeException(e);
            }

        },
                (Response.ErrorListener) error -> {
                    // make a Toast telling the user
                    // that something went wrong
                    Toast.makeText(this.mContext, "Se está reactivando el servidor, vuelve a intentarlo en un minuto", Toast.LENGTH_LONG).show();
                    Toast.makeText(this.mContext, this.room_name, Toast.LENGTH_LONG).show();
                    // log the error message in the error stream
                    error.printStackTrace();
                    Log.e("MainActivity", error.toString());
                    Log.e("MainActivity", url);
                    Log.e("MainActivity", entrada.toString());

                });
        volleyQueue.add(jsonObjectRequest);
        return null;
    }
    private void sendNotification(String text) {
        NotificationManager notificationManager =
                (NotificationManager) this.mContext.getSystemService(Context.NOTIFICATION_SERVICE);
        Notification.Builder builder;
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            NotificationChannel channel = new NotificationChannel("Beacon Reference Notifications",
                    "Beacon Reference Notifications", NotificationManager.IMPORTANCE_HIGH);
            channel.enableLights(true);
            channel.enableVibration(true);
            channel.setLockscreenVisibility(Notification.VISIBILITY_PUBLIC);
            notificationManager.createNotificationChannel(channel);
            builder = new Notification.Builder(this.mContext, channel.getId());
        }
        else {
            builder = new Notification.Builder(this.mContext);
            builder.setPriority(Notification.PRIORITY_HIGH);
        }

        TaskStackBuilder stackBuilder = TaskStackBuilder.create(this.mContext);
        stackBuilder.addNextIntent(new Intent(this.mContext, SplashActivity.class));
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

    @Override
    public void run() {
        getMedia(room_name);
    }

    public void ejec(){
        //Se ejecuta si es falso y no han pasado 30 min

        if (terminado != true && this.i < 6) {
            i = i+1;
            Toast.makeText(this.mContext, "Aún no se han cumplido las condiciones, ahora mismo hay " + ocupacion_actual.toString()+ " y debería bajar de " +factor.toString() + i.toString(), Toast.LENGTH_SHORT).show();
            ejecutarCodigo("Aún no se han cumplido las condiciones, ahora mismo hay " + ocupacion_actual.toString()+ " y debería bajar de " +factor.toString() + i.toString());

        }
        //Se ejecuta si han pasado al menos 30 min
        else if (this.i >= 6){
            Toast.makeText(this.mContext, this.media.toString(), Toast.LENGTH_LONG).show();
            ejecutarCodigo("Ha pasado media hora y la ocupación no ha bajado de " + factor.toString());
            NotificationActivity.stopScheduledTask();
        }
        else {
            ejecutarCodigo("La ocupación de " + this.room_name + " ha bajado del nivel de aforo establecido.");
            Toast.makeText(this.mContext, "Ya terminó", Toast.LENGTH_SHORT).show();
            NotificationActivity.stopScheduledTask();
        }

    }
}
