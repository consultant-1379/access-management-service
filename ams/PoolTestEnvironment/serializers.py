from rest_framework import serializers
from PoolTestEnvironment.models import Booking,Namespace,Cluster,Team

class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = '__all__' 

class BookingSerializer(serializers.ModelSerializer):
    team = TeamSerializer(read_only=True)
    class Meta:
        model = Booking
        fields = '__all__'

class BookingCreateSerializer(serializers.ModelSerializer):
    team = serializers.CharField()  # Expect a team name 
    namespace = serializers.CharField()  # Expect a namespace name instead of a namespace id
    booking_start_date = serializers.DateField(input_formats=['%d-%m-%Y'])
    booking_end_date = serializers.DateField(input_formats=['%d-%m-%Y'])

    class Meta:
        model = Booking
        fields = '__all__'

    def create(self, validated_data):
        # Remove the team name and namespace name from the validated data
        team_name = validated_data.pop('team')
        namespace_name = validated_data.pop('namespace')
        try:
            # Get the Team and Namespace instances
            team = Team.objects.get(name=team_name)
            namespace = Namespace.objects.get(name=namespace_name)
        except ObjectDoesNotExist:
            raise serializers.ValidationError({"detail": "No team or namespace found with these names."})
        # Create the Booking instance with the Team and Namespace instances
        booking = Booking.objects.create(team=team, namespace=namespace, **validated_data)
        return booking
    

class ClusterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cluster
        fields = '__all__'

class NamespaceSerializer(serializers.ModelSerializer):
    booking = BookingSerializer(read_only=True)
    # cluster = ClusterSerializer(read_only=True)

    class Meta:
        model = Namespace
        fields = ['name', 'booking']


